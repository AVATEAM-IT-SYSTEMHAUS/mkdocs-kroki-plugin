from mkdocs.exceptions import PluginError
from result import Err, Ok

from kroki.client import KrokiClient
from kroki.common import ErrorResult, ImageSrc, KrokiImageContext, MkDocsEventContext
from kroki.logging import log


class ContentRenderer:
    def __init__(self, kroki_client: KrokiClient, *, fail_fast: bool) -> None:
        self.fail_fast = fail_fast
        self.kroki_client = kroki_client

    def _get_media_type(self, file_ext: str) -> str:
        match file_ext:
            case "png":
                return "image/png"
            case "svg":
                return "image/svg+xml"
            case "jpeg":
                return "image/jpg"
            case "pdf":
                return "application/pdf"
            case _:
                raise NotImplementedError(file_ext)

    def _image_response(self, image_src: ImageSrc) -> str:
        media_type = self._get_media_type(image_src.file_ext)
        return f'<object name="Kroki" type="{media_type}" data="{image_src.url}" style="max-width:100%"></object>'

    def _err_response(self, err_result: ErrorResult, kroki_data: None | str = None) -> str:
        if ErrorResult.error is None:
            log.error("%s", err_result.err_msg)
        else:
            log.error("%s [raised by %s]", err_result.err_msg, err_result.error)

        if self.fail_fast:
            raise PluginError(err_result.err_msg) from err_result.error

        return (
            '<details open="">'
            f"<summary>{err_result.err_msg}</summary>"
            f'<p>{err_result.response_text or ""}</p>'
            f'<pre><code linenums="1">{kroki_data or ""}</code></pre>'
            "</details>"
        )

    def render_kroki_block(self, kroki_context: KrokiImageContext, context: MkDocsEventContext) -> str:
        match kroki_context.data:
            case Ok(kroki_data):
                match self.kroki_client.get_image_url(kroki_context, context):
                    case Ok(image_src):
                        return self._image_response(image_src)
                    case Err(err_result):
                        return self._err_response(err_result, kroki_data)
            case Err(err_result):
                return self._err_response(err_result)
