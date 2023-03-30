import re
import os
import textwrap

from mkdocs.config.base import Config as MkDocsBaseConfig
from mkdocs.config.config_options import (
    Type as MkDocsConfigType,
    URL as MkDocsConfigURL,
    Choice as MkDocsConfigChoice,
    Deprecated as MkDocsConfigDeprecated,
)
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin as MkDocsBasePlugin, get_plugin_logger
from mkdocs.structure.files import Files as MkDocsFiles
from mkdocs.structure.pages import Page as MkDocsPage
from pathlib import Path

from kroki.config import KrokiDiagramTypes
from kroki.client import KrokiClient, KrokiResponse

log = get_plugin_logger(__name__)


class DeprecatedDownloadImagesCompat(MkDocsConfigDeprecated):
    def pre_validation(self, config: "KrokiPluginConfig", key_name: str) -> None:
        """Set `HttpMethod: 'POST'`, if enabled"""
        if config.get(key_name) is None:
            return

        self.warnings.append(self.message.format(key_name))

        DownloadImages: bool = config.pop(key_name)
        if DownloadImages:
            config.HttpMethod = "POST"


class KrokiPluginConfig(MkDocsBaseConfig):
    ServerURL = MkDocsConfigURL(
        default=os.getenv("KROKI_SERVER_URL", "https://kroki.io")
    )
    EnableBlockDiag = MkDocsConfigType(bool, default=True)
    Enablebpmn = MkDocsConfigType(bool, default=True)
    EnableExcalidraw = MkDocsConfigType(bool, default=True)
    EnableMermaid = MkDocsConfigType(bool, default=True)
    EnableDiagramsnet = MkDocsConfigType(bool, default=False)
    HttpMethod = MkDocsConfigChoice(choices=["GET", "POST"], default="GET")
    UserAgent = MkDocsConfigType(str, default=f"{__name__}/0.6.1")
    FencePrefix = MkDocsConfigType(str, default="kroki-")
    FileTypes = MkDocsConfigType(list, default=["svg"])
    FileTypeOverrides = MkDocsConfigType(dict, default={})

    DownloadImages = DeprecatedDownloadImagesCompat(moved_to="HttpMethod: 'POST'")
    DownloadDir = MkDocsConfigDeprecated(removed=True)


class KrokiPlugin(MkDocsBasePlugin[KrokiPluginConfig]):
    diagram_types: KrokiDiagramTypes
    kroki_client: KrokiClient
    from_file_prefix = "@from_file:"
    global_config: MkDocsConfig
    _FENCE_RE = re.compile(r"(?P<fence>^(?P<indent>[ ]*)(?:````*|~~~~*))[ ]*"
                           r"(\.?(?P<lang>[\w#.+-]*)[ ]*)?"
                           r"(?P<opts>(?:[ ]?[a-zA-Z0-9\-_]+=[a-zA-Z0-9\-_]+)*)\n"
                           r"(?P<code>.*?)(?<=\n)"
                           r"(?P=fence)[ ]*$",
                           flags=re.IGNORECASE + re.DOTALL + re.MULTILINE)

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        log.debug(f"Configuring: {self.config}")

        self.diagram_types = KrokiDiagramTypes(
            self.config.EnableBlockDiag,
            self.config.Enablebpmn,
            self.config.EnableExcalidraw,
            self.config.EnableMermaid,
            self.config.EnableDiagramsnet,
            self.config.FileTypes,
            self.config.FileTypeOverrides,
        )

        self.kroki_client = KrokiClient(
            server_url=self.config.ServerURL,
            http_method=self.config.HttpMethod,
            user_agent=self.config.UserAgent,
            diagram_types=self.diagram_types,
        )

        self.global_config = config

        return config

    def _replace_kroki_block(
        self, kroki_type: str, kroki_options: str, kroki_data: str, files: MkDocsFiles, page: MkDocsPage
    ) -> str:

        if kroki_data.startswith(self.from_file_prefix):
            file_name = kroki_data.removeprefix(self.from_file_prefix).strip()
            file_path = Path(self.global_config.docs_dir) / file_name
            log.debug(f'Reading kroki block from file: "{file_path.absolute()}"')
            try:
                with open(file_path) as data_file:
                    kroki_data = data_file.read()
            except OSError:
                msg = f'Can\'t read file: "{file_path.absolute()}"'
                log.error(msg)
                return f"!!! error {msg}"

        kroki_diagram_options = (
            dict(x.split("=") for x in kroki_options.strip().split(" "))
            if kroki_options
            else {}
        )

        response: KrokiResponse = self.kroki_client.get_image_url(
            kroki_type, kroki_data, kroki_diagram_options, files, page
        )
        log.debug(f"{response}")
        if response.is_ok():
            return f"![Kroki]({response.image_url})"

        return f'!!! error "{response.err_msg}"\n\n```\n{kroki_data}\n```'

    def on_page_markdown(
        self, markdown: str, files: MkDocsFiles, page: MkDocsPage, **_kwargs
    ) -> str:
        log.debug(f"on_page_markdown [page: {page}]")

        key_types = self.diagram_types.diagram_types_supporting_file.keys()
        fence_prefix = self.config.FencePrefix

        def replace_kroki_block(match_obj: re.Match):
            kroki_type = match_obj.group('lang').lower()
            if kroki_type.startswith(fence_prefix):
                kroki_type = kroki_type[len(fence_prefix):]

                if kroki_type in key_types:
                    return match_obj.group('indent') + \
                        self._replace_kroki_block(kroki_type, match_obj.group('opts'),
                                                  textwrap.dedent(match_obj.group('code')),
                                                  files, page)

            # Not supported, skip over whole block
            return match_obj.group()

        return re.sub(self._FENCE_RE, replace_kroki_block, markdown)
