from mkdocs.plugins import BasePlugin as MkDocsBasePlugin

from kroki.cache import KrokiCache
from kroki.client import KrokiClient
from kroki.common import MkDocsConfig, MkDocsEventContext, MkDocsFiles, MkDocsPage
from kroki.config import KrokiPluginConfig
from kroki.diagram_types import KrokiDiagramTypes
from kroki.logging import log
from kroki.parsing import MarkdownParser
from kroki.render import ContentRenderer


class KrokiPlugin(MkDocsBasePlugin[KrokiPluginConfig]):
    renderer: ContentRenderer
    parser: MarkdownParser
    kroki_client: KrokiClient
    cache: KrokiCache
    diagram_types: KrokiDiagramTypes

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        log.debug("Configuring config: %s", self.config)

        self.diagram_types = KrokiDiagramTypes(
            self.config.fence_prefix,
            self.config.file_types,
            self.config.file_type_overrides,
            blockdiag_enabled=self.config.enable_block_diag,
            bpmn_enabled=self.config.enable_bpmn,
            excalidraw_enabled=self.config.enable_excalidraw,
            mermaid_enabled=self.config.enable_mermaid,
            diagramsnet_enabled=self.config.enable_diagramsnet,
        )

        self.cache = KrokiCache(cache_dir=self.config.cache_dir)

        self.kroki_client = KrokiClient(
            server_url=self.config.server_url,
            http_method=self.config.http_method,
            timeout_seconds=self.config.request_timeout,
            user_agent=self.config.user_agent,
            diagram_types=self.diagram_types,
            cache=self.cache,
        )
        self.parser = MarkdownParser(config.docs_dir, self.diagram_types)
        self.renderer = ContentRenderer(
            self.kroki_client,
            tag_format=self.config.tag_format,
            fail_fast=self.config.fail_fast,
            diagram_background_color_light=self.config.diagram_background_color_light,
            diagram_background_color_dark=self.config.diagram_background_color_dark,
        )

        return config

    def on_page_markdown(
        self,
        markdown: str,
        page: MkDocsPage,
        config: MkDocsConfig,
        files: MkDocsFiles,
    ) -> str:
        mkdocs_context = MkDocsEventContext(page=page, config=config, files=files)
        log.debug("on_page_content [%s]", mkdocs_context)

        return self.parser.replace_kroki_blocks(
            markdown, self.renderer.render_kroki_block, mkdocs_context
        )
