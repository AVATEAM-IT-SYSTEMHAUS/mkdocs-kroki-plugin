from mkdocs.exceptions import PluginError
from result import Err, Ok

from kroki.client import KrokiClient
from kroki.common import ErrorResult, ImageSrc, KrokiImageContext, MkDocsEventContext
from kroki.logging import log


class ContentRenderer:
    def __init__(self, kroki_client: KrokiClient, *, fail_fast: bool) -> None:
        self.fail_fast = fail_fast
        self.kroki_client = kroki_client

    def _image_response(self, image_src: ImageSrc) -> str:
        return f"![Kroki]({image_src.url})"

    def _err_response(self, err_result: ErrorResult, kroki_data: None | str = None) -> str:
        if ErrorResult.error is None:
            log.error("%s", err_result.err_msg)
        else:
            log.error("%s [raised by %s]", err_result.err_msg, err_result.error)

        if self.fail_fast:
            raise PluginError(err_result.err_msg) from err_result.error

        return f'!!! error "{err_result.err_msg}"\n{err_result.response_text or ""}\n```\n{kroki_data or ""}\n```'

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
