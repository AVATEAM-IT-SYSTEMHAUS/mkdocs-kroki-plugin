import base64
import zlib
import re
from mkdocs.plugins import BasePlugin
from mkdocs import config


class KrokiPlugin(BasePlugin):
    config_scheme = (
        ('ServerURL', config.config_options.Type(
            str, default='https://kroki.io')),
        ('EnableBlockDiag', config.config_options.Type(
            bool, default=True)),
        ('Enablebpmn', config.config_options.Type(
            bool, default=True)),
        ('EnableExcalidraw', config.config_options.Type(
            bool, default=True)),
        ('EnableMermaid', config.config_options.Type(
            bool, default=True)),
    )

    kroki_re = ""

    kroki_base = (
        "bytefield",
        "ditaa",
        "erd",
        "graphviz",
        "nomnoml",
        "plantuml",
        "c4plantuml",
        "svgbob",
        "vega",
        "vegalite",
        "wavedrom",
    )

    kroki_blockdiag = (
        "blockdiag",
        "seqdiag",
        "actdiag",
        "nwdiag",
        "packetdiag",
        "rackdiag",
    )

    kroki_bpmn = (
        "bpmn",
    )

    kroki_excalidraw = (
        "excalidraw",
    )

    kroki_mermaid = (
        "mermaid",
    )

    def on_config(self, config, **kwargs):
        self.kroki_re += "|".join(self.kroki_base)
        if self.config['EnableBlockDiag']:
            self.kroki_re += "|" + "|".join(self.kroki_blockdiag)
        if self.config['Enablebpmn']:
            self.kroki_re += "|" + "|".join(self.kroki_bpmn)
        if self.config['EnableExcalidraw']:
            self.kroki_re += "|" + "|".join(self.kroki_excalidraw)
        if self.config['EnableMermaid']:
            self.kroki_re += "|" + "|".join(self.kroki_mermaid)
        self.kroki_re = r'(?:```kroki-)(' + self.kroki_re + ')\n(.*?)(?:```)'
        return config

    def krokiurl(self, matchobj):
        kroki_type = matchobj.group(1).lower()
        kroki_path = base64.urlsafe_b64encode(
            zlib.compress(str.encode(matchobj.group(2)), 9)).decode()
        kroki_url = \
            "![Kroki](" + \
            self.config['ServerURL'] + \
            "/" + \
            kroki_type + \
            "/svg/" + \
            kroki_path + ")"

        return kroki_url

    def on_page_markdown(self, markdown, **kwargs):
        pattern = re.compile(self.kroki_re, flags=re.IGNORECASE+re.DOTALL)
        markdown = re.sub(pattern, self.krokiurl, markdown)
        return markdown
