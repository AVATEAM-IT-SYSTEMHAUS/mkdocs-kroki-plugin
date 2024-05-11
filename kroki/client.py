import base64
import zlib
from dataclasses import dataclass
from logging import DEBUG
from typing import Final

import requests
from mkdocs.exceptions import PluginError
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import Files as MkDocsFiles
from mkdocs.structure.pages import Page as MkDocsPage

from kroki.config import KrokiDiagramTypes
from kroki.util import DownloadedImage

log = get_plugin_logger(__name__)


MAX_URI_SIZE: Final[int] = 4096


@dataclass
class KrokiResponse:
    err_msg: None | str = None
    image_url: None | str = None

    def is_ok(self) -> bool:
        return self.image_url is not None and self.err_msg is None


class KrokiClient:
    def __init__(
        self,
        server_url: str,
        http_method: str,
        user_agent: str,
        diagram_types: KrokiDiagramTypes,
        *,
        fail_fast: bool,
    ) -> None:
        self.server_url = server_url
        self.http_method = http_method
        self.headers = {"User-Agent": user_agent}
        self.diagram_types = diagram_types
        self.fail_fast = fail_fast

        log.debug("Client initialized", extra={"http_method": self.http_method, "server_url": self.server_url})

    def _kroki_url_base(self, kroki_type: str) -> str:
        file_type = self.diagram_types.get_file_ext(kroki_type)
        return f"{self.server_url}/{kroki_type}/{file_type}"

    def _kroki_url_get(
        self,
        kroki_type: str,
        kroki_diagram_data: str,
        kroki_diagram_options: dict[str, str],
    ) -> KrokiResponse:
        kroki_data_param = base64.urlsafe_b64encode(zlib.compress(str.encode(kroki_diagram_data), 9)).decode()

        kroki_query_param = (
            "&".join([f"{k}={v}" for k, v in kroki_diagram_options.items()]) if len(kroki_diagram_options) > 0 else ""
        )

        kroki_url = self._kroki_url_base(kroki_type)
        image_url = f"{kroki_url}/{kroki_data_param}?{kroki_query_param}"
        if len(image_url) >= MAX_URI_SIZE:
            log.warning("Kroki may not be able to read the data completely!", extra={"data_len": len(image_url)})

        log.debug("Image url: %s", image_url)
        return KrokiResponse(image_url=image_url)

    def _kroki_post(
        self,
        kroki_type: str,
        kroki_diagram_data: str,
        kroki_diagram_options: dict[str, str],
        files: MkDocsFiles,
        page: MkDocsPage,
    ) -> KrokiResponse:
        url = self._kroki_url_base(kroki_type)

        log.debug("POST %s", url)
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={
                    "diagram_source": kroki_diagram_data,
                    "diagram_options": kroki_diagram_options,
                },
                timeout=10,
            )
        except requests.RequestException as error:
            error_message = f"Request error [url:{url}]: {error}"
            log.exception(error_message, stack_info=log.isEnabledFor(DEBUG))
            if self.fail_fast:
                raise PluginError(error_message) from error

            return KrokiResponse(err_msg=error_message)

        if response.status_code == requests.codes.ok:
            downloaded_image = DownloadedImage(
                response.content,
                self.diagram_types.get_file_ext(kroki_type),
                kroki_diagram_options,
            )
            downloaded_image.save(files, page)
            return KrokiResponse(image_url=downloaded_image.file_name)

        error_message = (
            "Diagram error!"
            if response.status_code == requests.codes.bad_request
            else f"Could not retrieve image data, got: {response}"
        )
        log.error(error_message)
        if self.fail_fast:
            raise PluginError(error_message)

        return KrokiResponse(err_msg=error_message)

    def get_image_url(
        self,
        kroki_type: str,
        kroki_diagram_data: str,
        kroki_diagram_options: dict[str, str],
        files: MkDocsFiles,
        page: MkDocsPage,
    ) -> KrokiResponse:
        if self.http_method == "GET":
            return self._kroki_url_get(kroki_type, kroki_diagram_data, kroki_diagram_options)

        return self._kroki_post(kroki_type, kroki_diagram_data, kroki_diagram_options, files, page)
