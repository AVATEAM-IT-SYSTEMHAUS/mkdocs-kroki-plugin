from xml.etree import ElementTree as XmlElementTree

from defusedxml import ElementTree as DefuseElementTree
from mkdocs.exceptions import PluginError
from result import Err, Ok

from kroki.client import KrokiClient
from kroki.common import ErrorResult, ImageSrc, KrokiImageContext, MkDocsEventContext
from kroki.logging import log


class ContentRenderer:
    def __init__(self, kroki_client: KrokiClient, tag_format: str, *, fail_fast: bool) -> None:
        self.fail_fast = fail_fast
        self.kroki_client = kroki_client
        self.tag_format = tag_format

    def _get_object_media_type(self, file_ext: str) -> str:
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
                err_msg = f"Not implemented: '{file_ext}"
                raise PluginError(err_msg)

    @classmethod
    def _svg_data(cls, image_src: ImageSrc) -> str:
        if image_src.file_content is None:
            err_msg = "Cannot include empty SVG data"
            raise PluginError(err_msg)

        XmlElementTree.register_namespace("", "http://www.w3.org/2000/svg")
        XmlElementTree.register_namespace("xlink", "http://www.w3.org/1999/xlink")
        svg_tag = DefuseElementTree.fromstring(
            image_src.file_content.decode("UTF-8"),
        )
        svg_tag.attrib["preserveAspectRatio"] = "xMaxYMax meet"
        svg_tag.attrib["id"] = "Kroki"

        return DefuseElementTree.tostring(svg_tag, short_empty_elements=True).decode()

    def _image_response(self, image_src: ImageSrc) -> str:
        tag_format = self.tag_format
        if tag_format == "svg":
            if image_src.file_ext != "svg":
                log.warning("Cannot render '%s' in svg tag -> using img tag.", image_src.url)
                tag_format = "img"
            if image_src.file_content is None:
                log.warning("Cannot render missing data in svg tag -> using img tag.")
                tag_format = "img"

        match tag_format:
            case "object":
                media_type = self._get_object_media_type(image_src.file_ext)
                return f'<object id="Kroki" type="{media_type}" data="{image_src.url}" style="max-width:100%"></object>'
            case "svg":
                return ContentRenderer._svg_data(image_src)
            case "img":
                return f'<img alt="Kroki" src="{image_src.url}">'
            case _:
                err_msg = "Unknown tag format set."
                raise PluginError(err_msg)

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
