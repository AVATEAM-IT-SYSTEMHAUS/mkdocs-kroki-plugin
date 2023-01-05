from functools import partial
from mkdocs.plugins import log

info = partial(log.info, f'{__name__} %s')


class KrokiDiagramTypes():
    kroki_base = {
        "bytefield": ["svg"],
        "ditaa": ["png", "svg"],
        "erd": ["png", "svg", "jpeg", "pdf"],
        "graphviz": ["png", "svg", "jpeg", "pdf"],
        "nomnoml": ["svg"],
        "plantuml": ["png", "svg", "jpeg", "base64"],
        "structurizr": ["png", "svg"],
        "c4plantuml": ["png", "svg", "jpeg", "base64"],
        "svgbob": ["svg"],
        "vega": ["png", "svg", "pdf"],
        "vegalite": ["png", "svg", "pdf"],
        "wavedrom": ["svg"],
        "pikchr": ["svg"],
        "umlet": ["png", "svg"],
    }

    kroki_blockdiag = {
        "blockdiag": ["png", "svg", "pdf"],
        "seqdiag": ["png", "svg", "pdf"],
        "actdiag": ["png", "svg", "pdf"],
        "nwdiag": ["png", "svg", "pdf"],
        "packetdiag": ["png", "svg", "pdf"],
        "rackdiag": ["png", "svg", "pdf"],
    }

    kroki_bpmn = {
        "bpmn": ["svg"],
    }

    kroki_excalidraw = {
        "excalidraw": ["svg"],
    }

    kroki_mermaid = {
        "mermaid": ["png", "svg"],
    }

    kroki_diagramsnet = {
        "diagramsnet": ["svg"],
    }

    def __init__(self, blockdiag_enabled, bpmn_enabled, excalidraw_enabled,
                 mermaid_enabled, diagramsnet_enabled, file_types, file_type_overrides):
        diagram_types = self.kroki_base.copy()

        if blockdiag_enabled:
            diagram_types.update(self.kroki_blockdiag)
        if bpmn_enabled:
            diagram_types.update(self.kroki_bpmn)
        if excalidraw_enabled:
            diagram_types.update(self.kroki_excalidraw)
        if mermaid_enabled:
            diagram_types.update(self.kroki_mermaid)
        if diagramsnet_enabled:
            diagram_types.update(self.kroki_diagramsnet)

        self.diagram_types_supporting_file = {}

        for diagram_type, diagram_file_types in diagram_types.items():
            diagram_file_type = next(filter(lambda file: file in diagram_file_types, file_types), None)
            if diagram_file_type is not None:
                self.diagram_types_supporting_file[diagram_type] = next(
                    filter(lambda file: file in diagram_file_types, file_types), None)

        for diagram_type, diagram_file_type in file_type_overrides.items():
            self.diagram_types_supporting_file[diagram_type] = diagram_file_type

        info(f'File and Diagram types configured: {self.diagram_types_supporting_file}')

    def get_block_regex(self, fence_prefix):
        diagram_types_re = "|".join(self.diagram_types_supporting_file.keys())
        return rf'(?:```{fence_prefix})({diagram_types_re})((?:\s?[a-zA-Z0-9\-_]+=[a-zA-Z0-9\-_]+)*)\n(.*?)(?:```)'

    def get_file_ext(self, kroki_type):
        return self.diagram_types_supporting_file[kroki_type]
