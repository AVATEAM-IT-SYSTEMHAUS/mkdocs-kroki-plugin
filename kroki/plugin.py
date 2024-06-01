from mkdocs.plugins import BasePlugin as MkDocsBasePlugin

from kroki.client import KrokiClient
from kroki.common import MkDocsConfig, MkDocsEventContext, MkDocsFiles, MkDocsPage
from kroki.config import KrokiPluginConfig
from kroki.diagram_types import KrokiDiagramTypes
from kroki.logging import log
from kroki.parsing import MarkdownParser
from kroki.render import ContentRenderer


class KrokiPlugin(MkDocsBasePlugin[KrokiPluginConfig]):
    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        log.debug("Configuring config: %s", self.config)

        self.diagram_types = KrokiDiagramTypes(
            self.config.FencePrefix,
            self.config.FileTypes,
            self.config.FileTypeOverrides,
            blockdiag_enabled=self.config.EnableBlockDiag,
            bpmn_enabled=self.config.Enablebpmn,
            excalidraw_enabled=self.config.EnableExcalidraw,
            mermaid_enabled=self.config.EnableMermaid,
            diagramsnet_enabled=self.config.EnableDiagramsnet,
        )
        self.kroki_client = KrokiClient(
            server_url=self.config.ServerURL,
            http_method=self.config.HttpMethod,
            user_agent=self.config.UserAgent,
            diagram_types=self.diagram_types,
        )
        self.parser = MarkdownParser(config.docs_dir, self.diagram_types)
        self.renderer = ContentRenderer(self.kroki_client, fail_fast=self.config.FailFast)

        return config

    def on_page_markdown(self, markdown: str, page: MkDocsPage, config: MkDocsConfig, files: MkDocsFiles) -> str:
        mkdocs_context = MkDocsEventContext(page=page, config=config, files=files)
        log.debug("on_page_content [%s]", mkdocs_context)

        return self.parser.replace_kroki_blocks(markdown, self.renderer.render_kroki_block, mkdocs_context)
