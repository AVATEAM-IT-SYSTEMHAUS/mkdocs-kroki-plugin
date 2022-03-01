class KrokiDiagramTypes():
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
        "pikchr",
        "umlet",
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

    def __init__(self, blockdiag_enabled, bpmn_enabled, excalidraw_enabled, mermaid_enabled):
        self.diagram_types = self.kroki_base

        if blockdiag_enabled:
            self.diagram_types += self.kroki_blockdiag
        if bpmn_enabled:
            self.diagram_types += self.kroki_bpmn
        if excalidraw_enabled:
            self.diagram_types += self.kroki_excalidraw
        if mermaid_enabled:
            self.diagram_types += self.kroki_mermaid

    def get_block_regex(self, fence_prefix):
        diagram_types_re = "|".join(self.diagram_types)
        return rf'(?:```{fence_prefix})({diagram_types_re})\n(.*?)(?:```)'
