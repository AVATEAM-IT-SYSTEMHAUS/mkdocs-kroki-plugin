import os

from mkdocs.config import config_options
from mkdocs.config.base import (
    ConfigErrors as MkDocsConfigErrors,
    ConfigWarnings as MkDocsConfigWarnings,
    Config as MkDocsBaseConfig,
)

from kroki import __version__
from kroki.logging import log


class KrokiPluginConfig(MkDocsBaseConfig):
    server_url = config_options.URL(
        default=os.getenv("KROKI_SERVER_URL", "https://kroki.io")
    )
    enable_block_diag = config_options.Type(bool, default=True)
    enable_bpmn = config_options.Type(bool, default=True)
    enable_excalidraw = config_options.Type(bool, default=True)
    enable_mermaid = config_options.Type(bool, default=True)
    enable_diagramsnet = config_options.Type(bool, default=False)
    http_method = config_options.Choice(choices=["GET", "POST"], default="GET")
    request_timeout = config_options.Type(int, default=30)
    user_agent = config_options.Type(str, default=f"{__name__}/{__version__}")
    fence_prefix = config_options.Type(str, default="kroki-")
    file_types = config_options.Type(list, default=["svg"])
    file_type_overrides = config_options.Type(dict, default={})
    tag_format = config_options.Choice(choices=["img", "object", "svg"], default="img")
    fail_fast = config_options.Type(bool, default=False)
    cache_dir = config_options.Optional(config_options.Type(str))
    download_dir = config_options.Deprecated(removed=True)
    diagram_background_color_light = config_options.Optional(config_options.Type(str))
    diagram_background_color_dark = config_options.Optional(config_options.Type(str))

    def validate(self) -> tuple[MkDocsConfigErrors, MkDocsConfigWarnings]:
        result = super().validate()

        if self["tag_format"] == "svg" and self["http_method"] != "POST":
            log.info("Setting Http method to POST to retrieve svg data for inlining.")
            self["http_method"] = "POST"

        return result
