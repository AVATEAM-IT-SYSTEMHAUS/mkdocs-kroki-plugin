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
    ServerURL = config_options.URL(
        default=os.getenv("KROKI_SERVER_URL", "https://kroki.io")
    )
    EnableBlockDiag = config_options.Type(bool, default=True)
    EnableBpmn = config_options.Type(bool, default=True)
    EnableExcalidraw = config_options.Type(bool, default=True)
    EnableMermaid = config_options.Type(bool, default=True)
    EnableDiagramsnet = config_options.Type(bool, default=False)
    HttpMethod = config_options.Choice(choices=["GET", "POST"], default="GET")
    RequestTimeout = config_options.Type(int, default=30)
    UserAgent = config_options.Type(str, default=f"{__name__}/{__version__}")
    FencePrefix = config_options.Type(str, default="kroki-")
    FileTypes = config_options.Type(list, default=["svg"])
    FileTypeOverrides = config_options.Type(dict, default={})
    TagFormat = config_options.Choice(choices=["img", "object", "svg"], default="img")
    FailFast = config_options.Type(bool, default=False)
    CacheDir = config_options.Optional(config_options.Type(str))
    DownloadDir = config_options.Deprecated(removed=True)

    def validate(self) -> tuple[MkDocsConfigErrors, MkDocsConfigWarnings]:
        result = super().validate()

        if self["TagFormat"] == "svg" and self["HttpMethod"] != "POST":
            log.info("Setting Http method to POST to retrieve svg data for inlining.")
            self["HttpMethod"] = "POST"

        return result
