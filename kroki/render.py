import asyncio
from xml.etree import ElementTree as XmlElementTree

from defusedxml import ElementTree as DefuseElementTree
from mkdocs.exceptions import PluginError
from result import Err, Ok

from kroki.client import KrokiClient
from kroki.common import ErrorResult, ImageSrc, KrokiImageContext, MkDocsEventContext
from kroki.logging import log


def _get_object_media_type(file_ext: str) -> str:
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


class ContentRenderer:
    def __init__(
        self,
        kroki_client: KrokiClient,
        tag_format: str,
        *,
        fail_fast: bool,
        diagram_background_color_light: str | None = None,
        diagram_background_color_dark: str | None = None,
    ) -> None:
        self.fail_fast = fail_fast
        self.kroki_client = kroki_client
        self.tag_format = tag_format
        self.diagram_background_color_light = diagram_background_color_light
        self.diagram_background_color_dark = diagram_background_color_dark

    def _build_style_attr(self, plugin_options: dict) -> str:
        """Build inline style attribute from plugin options."""
        styles = self._build_styles(plugin_options)
        if not styles:
            return ""
        return f' style="{"; ".join(styles)}"'

    def _build_styles(self, plugin_options: dict) -> list[str]:
        """Build list of CSS styles from plugin options, merging global defaults."""
        styles = []
        if "display-width" in plugin_options:
            styles.append(f"width: {plugin_options['display-width']}")
        if "display-height" in plugin_options:
            styles.append(f"height: {plugin_options['display-height']}")
        if "display-align" in plugin_options:
            align = plugin_options["display-align"]
            styles.append("display: block")
            if align == "center":
                styles.append("margin-left: auto")
                styles.append("margin-right: auto")
            elif align == "right":
                styles.append("margin-left: auto")
                styles.append("margin-right: 0")
            elif align == "left":
                styles.append("margin-left: 0")
                styles.append("margin-right: auto")

        # Background color: per-diagram options override global defaults
        bg_light = plugin_options.get("bg-light", self.diagram_background_color_light)
        bg_dark = plugin_options.get("bg-dark", self.diagram_background_color_dark)

        if bg_light and bg_dark:
            styles.append(f"background: light-dark({bg_light}, {bg_dark})")
        elif bg_light:
            styles.append(f"background: {bg_light}")
        elif bg_dark:
            styles.append(f"background: {bg_dark}")

        return styles

    def _svg_data(self, image_src: ImageSrc, plugin_options: dict) -> str:
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

        # Build inline style for display and background options
        styles = self._build_styles(plugin_options)
        if styles:
            svg_tag.attrib["style"] = "; ".join(styles)

        svg_str = DefuseElementTree.tostring(
            svg_tag, short_empty_elements=True
        ).decode()
        # Remove blank lines to prevent Markdown parser from breaking the SVG.
        # Wrap in <div> because Python-Markdown does not recognize <svg> as a
        # block-level element, causing it to be wrapped in <p> tags otherwise.
        svg_no_blanks = "\n".join(line for line in svg_str.splitlines() if line.strip())
        return f"<div>{svg_no_blanks}</div>"

    def _image_response(self, image_src: ImageSrc, plugin_options: dict) -> str:
        tag_format = self.tag_format
        if tag_format == "svg":
            if image_src.file_ext != "svg":
                log.warning(
                    "Cannot render '%s' in svg tag -> using img tag.", image_src.url
                )
                tag_format = "img"
            if image_src.file_content is None:
                log.warning("Cannot render missing data in svg tag -> using img tag.")
                tag_format = "img"

        style_attr = self._build_style_attr(plugin_options)

        match tag_format:
            case "object":
                media_type = _get_object_media_type(image_src.file_ext)
                return f'<object id="Kroki" type="{media_type}" data="{image_src.url}"{style_attr}></object>'
            case "svg":
                return self._svg_data(image_src, plugin_options)
            case "img":
                return f'<img alt="Kroki" src="{image_src.url}"{style_attr} />'
            case _:
                err_msg = "Unknown tag format set."
                raise PluginError(err_msg)

    def _err_response(
        self, err_result: ErrorResult, kroki_data: None | str = None
    ) -> str:
        if ErrorResult.error is None:
            log.error("%s", err_result.err_msg)
        else:
            log.error("%s [raised by %s]", err_result.err_msg, err_result.error)

        if self.fail_fast:
            raise PluginError(err_result.err_msg) from err_result.error

        return (
            '<details open="">'
            f"<summary>{err_result.err_msg}</summary>"
            f"<p>{err_result.response_text or ''}</p>"
            f'<pre><code linenums="1">{kroki_data or ""}</code></pre>'
            "</details>"
        )

    def _dual_image_response(
        self,
        image_src_light: ImageSrc,
        image_src_dark: ImageSrc,
        plugin_options: dict,
    ) -> str:
        style_attr = self._build_style_attr(plugin_options)
        return (
            f'<img alt="Kroki" src="{image_src_light.url}#only-light"{style_attr} />'
            f'<img alt="Kroki" src="{image_src_dark.url}#only-dark"{style_attr} />'
        )

    async def _render_dual(
        self, kroki_context: KrokiImageContext, context: MkDocsEventContext
    ) -> str:
        if self.tag_format != "img":
            log.warning(
                "Dual theme styles (styles_light/styles_dark) require tag_format 'img'. "
                "Falling back to light-mode styles only."
            )
            match kroki_context.data:
                case Ok(kroki_data):
                    match await self.kroki_client.get_image_url(kroki_context, context):
                        case Ok(image_src):
                            return self._image_response(
                                image_src, kroki_context.plugin_options
                            )
                        case Err(err_result):
                            return self._err_response(err_result, kroki_data)
                case Err(err_result):
                    return self._err_response(err_result)

        # Build a dark-mode context to fetch the dark image
        assert kroki_context.data_dark is not None
        dark_context = KrokiImageContext(
            kroki_type=kroki_context.kroki_type,
            options=kroki_context.options,
            plugin_options=kroki_context.plugin_options,
            data=kroki_context.data_dark,
        )

        match kroki_context.data:
            case Err(err_result):
                return self._err_response(err_result)

        match kroki_context.data_dark:
            case Err(err_result):
                return self._err_response(err_result)

        light_result, dark_result = await asyncio.gather(
            self.kroki_client.get_image_url(kroki_context, context),
            self.kroki_client.get_image_url(dark_context, context),
        )

        match light_result:
            case Err(err_result):
                return self._err_response(err_result, kroki_context.data.unwrap())
        match dark_result:
            case Err(err_result):
                return self._err_response(err_result, dark_context.data.unwrap())

        return self._dual_image_response(
            light_result.unwrap(),
            dark_result.unwrap(),
            kroki_context.plugin_options,
        )

    async def render_kroki_block(
        self, kroki_context: KrokiImageContext, context: MkDocsEventContext
    ) -> str:
        if kroki_context.data_dark is not None:
            return await self._render_dual(kroki_context, context)

        match kroki_context.data:
            case Ok(kroki_data):
                match await self.kroki_client.get_image_url(kroki_context, context):
                    case Ok(image_src):
                        return self._image_response(
                            image_src, kroki_context.plugin_options
                        )
                    case Err(err_result):
                        return self._err_response(err_result, kroki_data)
            case Err(err_result):
                return self._err_response(err_result)
