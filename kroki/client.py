import base64
import requests
import zlib

from dataclasses import dataclass
from logging import DEBUG
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import Files as MkDocsFiles
from mkdocs.structure.pages import Page as MkDocsPage
from typing import Optional

from kroki.config import KrokiDiagramTypes
from kroki.util import DownloadedImage

log = get_plugin_logger(__name__)


@dataclass
class KrokiResponse:
    err_msg: Optional[str] = None
    image_url: Optional[str] = None

    def is_ok(self) -> bool:
        return self.image_url is not None and self.err_msg is None


class KrokiClient:
    def __init__(
        self,
        server_url: str,
        http_method: str,
        user_agent: str,
        diagram_types: KrokiDiagramTypes,
    ) -> None:
        self.server_url = server_url
        self.http_method = http_method
        self.headers = {"User-Agent": user_agent}
        self.diagram_types = diagram_types

        log.debug(f"Client initialized: {self.http_method}, {self.server_url}")

    def _kroki_url_base(self, kroki_type: str) -> str:
        file_type = self.diagram_types.get_file_ext(kroki_type)
        return f"{self.server_url}/{kroki_type}/{file_type}"

    def _kroki_url_get(
        self,
        kroki_type: str,
        kroki_diagram_data: str,
        kroki_diagram_options: dict[str, str],
    ) -> KrokiResponse:
        kroki_data_param = base64.urlsafe_b64encode(
            zlib.compress(str.encode(kroki_diagram_data), 9)
        ).decode()

        kroki_query_param = (
            "&".join([f"{k}={v}" for k, v in kroki_diagram_options.items()])
            if len(kroki_diagram_options) > 0
            else ""
        )
        if len(kroki_data_param) >= 4096:
            log.warning(
                f"Length of encoded diagram is {len(kroki_data_param)}. "
                "Kroki may not be able to read the data completely!"
            )

        kroki_url = self._kroki_url_base(kroki_type)
        log.debug(f"{kroki_url}/{kroki_data_param}?{kroki_query_param}")
        return KrokiResponse(
            image_url=f"{kroki_url}/{kroki_data_param}?{kroki_query_param}"
        )

    def _kroki_post(
        self,
        kroki_type: str,
        kroki_diagram_data: str,
        kroki_diagram_options: dict[str, str],
        files: MkDocsFiles,
        page: MkDocsPage,
    ) -> KrokiResponse:
        try:
            url = self._kroki_url_base(kroki_type)

            log.debug(f"_kroki_post [POST {url}]")
            response = requests.post(
                url,
                headers=self.headers,
                json={
                    "diagram_source": kroki_diagram_data,
                    "diagram_options": kroki_diagram_options,
                },
            )

            if response.status_code == requests.codes.ok:
                downloaded_image = DownloadedImage(
                    response.content,
                    self.diagram_types.get_file_ext(kroki_type),
                    kroki_diagram_options,
                )
                downloaded_image.save(files, page)
                return KrokiResponse(image_url=downloaded_image.file_name)

            elif response.status_code == 400:
                return KrokiResponse(err_msg="Diagram error!")
            else:
                log.error(f"Could not retrieve image data, got: {response}")

        except Exception as exception:
            log.error(exception, stack_info=log.isEnabledFor(DEBUG))

        return KrokiResponse(err_msg="Could not render!")

    def get_image_url(
        self,
        kroki_type: str,
        kroki_diagram_data: str,
        kroki_diagram_options: dict[str, str],
        files: MkDocsFiles,
        page: MkDocsPage,
    ) -> KrokiResponse:
        if self.http_method == "GET":
            return self._kroki_url_get(
                kroki_type, kroki_diagram_data, kroki_diagram_options
            )

        return self._kroki_post(
            kroki_type, kroki_diagram_data, kroki_diagram_options, files, page
        )
