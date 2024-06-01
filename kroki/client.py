import base64
import textwrap
import zlib
from os import makedirs, path
from typing import Final
from uuid import NAMESPACE_OID, uuid3

import requests
from result import Err, Ok, Result

from kroki.common import ErrorResult, ImageSrc, KrokiImageContext, MkDocsEventContext, MkDocsFile
from kroki.diagram_types import KrokiDiagramTypes
from kroki.logging import log

MAX_URI_SIZE: Final[int] = 4096
FILE_PREFIX: Final[str] = "kroki-generated-"


class DownloadedContent:
    def _ugly_temp_excalidraw_fix(self) -> None:
        """TODO: remove me, when excalidraw container works again..
        ref: https://github.com/excalidraw/excalidraw/issues/7366"""
        self.file_content = self.file_content.replace(
            b"https://unpkg.com/@excalidraw/excalidraw@undefined/dist",
            b"https://unpkg.com/@excalidraw/excalidraw@0.17.1/dist",
        )

    def __init__(self, file_content: bytes, file_extension: str, additional_metadata: None | dict) -> None:
        file_uuid = uuid3(NAMESPACE_OID, f"{additional_metadata}{file_content}")

        self.file_name = f"{FILE_PREFIX}{file_uuid}.{file_extension}"
        self.file_content = file_content
        self._ugly_temp_excalidraw_fix()

    def save(self, context: MkDocsEventContext) -> None:
        # wherever MkDocs wants to host or build, we plant the image next
        # to the generated static page
        page_abs_dest_dir = path.dirname(context.page.file.abs_dest_path)
        makedirs(page_abs_dest_dir, exist_ok=True)

        file_path = path.join(page_abs_dest_dir, self.file_name)

        log.debug("Saving downloaded data: %s", file_path)
        with open(file_path, "wb") as file:
            file.write(self.file_content)

        # make MkDocs believe that the file was present from the beginning
        file_src_uri = path.join(path.dirname(context.page.file.src_uri), self.file_name)
        file_dest_uri = path.join(path.dirname(context.page.file.dest_uri), self.file_name)

        dummy_file = MkDocsFile(
            path=file_src_uri,
            src_dir="",
            dest_dir="",
            use_directory_urls=False,
            dest_uri=file_dest_uri,
        )
        # MkDocs will not copy the file in this case
        dummy_file.abs_src_path = dummy_file.abs_dest_path = file_path

        log.debug("Appending dummy mkdocs file: %s", dummy_file)
        context.files.append(dummy_file)


class KrokiClient:
    def __init__(self, server_url: str, http_method: str, user_agent: str, diagram_types: KrokiDiagramTypes) -> None:
        self.server_url = server_url
        self.http_method = http_method
        self.headers = {"User-Agent": user_agent}
        self.diagram_types = diagram_types

        log.debug("Client initialized [http_method: %s, server_url: %s]", self.http_method, self.server_url)

    def _kroki_url_base(self, kroki_type: str) -> str:
        return f"{self.server_url}/{kroki_type}"

    def _get_file_ext(self, kroki_type: str) -> str:
        return self.diagram_types.get_file_ext(kroki_type)

    def _kroki_url_get(self, kroki_context: KrokiImageContext) -> Result[ImageSrc, ErrorResult]:
        kroki_data_param = base64.urlsafe_b64encode(zlib.compress(str.encode(kroki_context.data.unwrap()), 9)).decode()

        kroki_query_param = (
            "&".join([f"{k}={v}" for k, v in kroki_context.options.items()]) if len(kroki_context.options) > 0 else ""
        )

        kroki_endpoint = self._kroki_url_base(kroki_type=kroki_context.kroki_type)
        file_ext = self._get_file_ext(kroki_context.kroki_type)
        image_url = f"{kroki_endpoint}/{file_ext}/{kroki_data_param}?{kroki_query_param}"
        if len(image_url) >= MAX_URI_SIZE:
            log.warning("Kroki may not be able to read the data completely! [data_len: %i]", len(image_url))

        log.debug("Image url: %s", textwrap.shorten(image_url, 50))
        return Ok(ImageSrc(url=image_url, file_ext=file_ext))

    def _kroki_post(
        self, kroki_context: KrokiImageContext, context: MkDocsEventContext
    ) -> Result[ImageSrc, ErrorResult]:
        kroki_endpoint = self._kroki_url_base(kroki_context.kroki_type)
        file_ext = self._get_file_ext(kroki_context.kroki_type)
        url = f"{kroki_endpoint}/{file_ext}"

        log.debug("POST %s", textwrap.shorten(url, 50))
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={
                    "diagram_source": kroki_context.data.unwrap(),
                    "diagram_options": kroki_context.options,
                },
                timeout=10,
                stream=True,
            )
        except requests.RequestException as error:
            return Err(ErrorResult(err_msg=f"Request error [url:{url}]: {error}", error=error))

        if response.status_code == requests.codes.ok:
            downloaded_image = DownloadedContent(
                response.content,
                file_ext,
                kroki_context.options,
            )
            downloaded_image.save(context)
            return Ok(ImageSrc(url=downloaded_image.file_name, file_ext=file_ext))

        if response.status_code == requests.codes.bad_request:
            return Err(ErrorResult(err_msg="Diagram error!", response_text=response.text))

        return Err(
            ErrorResult(err_msg=f"Could not retrieve image data, got: {response.reason} [{response.status_code}]")
        )

    def get_image_url(
        self, kroki_context: KrokiImageContext, context: MkDocsEventContext
    ) -> Result[ImageSrc, ErrorResult]:
        if self.http_method == "GET":
            return self._kroki_url_get(kroki_context)

        return self._kroki_post(kroki_context, context)
