import os

from mkdocs.config import config_options
from mkdocs.config.base import (
    Config as MkDocsBaseConfig,
)
from mkdocs.config.base import (
    ConfigErrors as MkDocsConfigErrors,
)
from mkdocs.config.base import (
    ConfigWarnings as MkDocsConfigWarnings,
)

from kroki import version
from kroki.logging import log


class DeprecatedDownloadImagesCompat(config_options.Deprecated):
    def pre_validation(self, config: MkDocsBaseConfig, key_name: str) -> None:
        """Set `HttpMethod: 'POST'`, if enabled"""
        if not isinstance(config, KrokiPluginConfig):
            return

        if config.get(key_name) is None:
            return

        self.warnings.append(self.message.format(key_name))

        download_images: bool = config.pop(key_name)
        if download_images:
            config.HttpMethod = "POST"


class KrokiPluginConfig(MkDocsBaseConfig):
    ServerURL = config_options.URL(default=os.getenv("KROKI_SERVER_URL", "https://kroki.io"))
    EnableBlockDiag = config_options.Type(bool, default=os.getenv("KROKI_ENABLE_BLOCK_DIAG", "True").lower() in ("true", "1", "t"))
    EnableBpmn = config_options.Type(bool, default=os.getenv("KROKI_ENABLE_BPMN", "True").lower() in ("true", "1", "t"))
    EnableExcalidraw = config_options.Type(bool, default=os.getenv("KROKI_ENABLE_EXCALIDRAW", "True").lower() in ("true", "1", "t"))
    EnableMermaid = config_options.Type(bool, default=os.getenv("KROKI_ENABLE_MERMAID", "True").lower() in ("true", "1", "t"))
    EnableDiagramsnet = config_options.Type(bool, default=os.getenv("KROKI_ENABLE_DIAGRAMSNET", "False").lower() in ("true", "1", "t"))
    HttpMethod = config_options.Choice(choices=["GET", "POST"], default=os.getenv("KROKI_HTTP_METHOD", "GET"))
    UserAgent = config_options.Type(str, default=os.getenv("KROKI_USER_AGENT", f"{__name__}/{version}"))
    FencePrefix = config_options.Type(str, default=os.getenv("KROKI_FENCE_PREFIX", "kroki-"))
    FileTypes = config_options.Type(list, default=os.getenv("KROKI_FILE_TYPES", "svg").split(","))
    FileTypeOverrides = config_options.Type(dict, default=eval(os.getenv("KROKI_FILE_TYPE_OVERRIDES", "{}")))
    TagFormat = config_options.Choice(choices=["img", "object", "svg"], default=os.getenv("KROKI_TAG_FORMAT", "img"))
    FailFast = config_options.Type(bool, default=os.getenv("KROKI_FAIL_FAST", "False").lower() in ("true", "1", "t"))

    DownloadImages = DeprecatedDownloadImagesCompat(moved_to="HttpMethod: 'POST'")
    Enablebpmn = config_options.Deprecated(moved_to="EnableBpmn")
    DownloadDir = config_options.Deprecated(removed=True)

    def validate(self) -> tuple[MkDocsConfigErrors, MkDocsConfigWarnings]:
        result = super().validate()

        if self["TagFormat"] == "svg" and self["HttpMethod"] != "POST":
            log.info("Setting Http method to POST to retrieve svg data for inlining.")
            self["HttpMethod"] = "POST"

        return result
