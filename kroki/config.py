from typing import ClassVar

from mkdocs.plugins import get_plugin_logger

log = get_plugin_logger(__name__)


class KrokiDiagramTypes:
    kroki_base: ClassVar[dict[str, list[str]]] = {
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
        "d2": ["svg"],
        "dbml": ["svg"],
        "tikz": ["png", "svg", "jpeg", "pdf"],
        "symbolator": ["svg"],
        "wireviz": ["png", "svg"],
    }

    kroki_blockdiag: ClassVar[dict[str, list[str]]] = {
        "blockdiag": ["png", "svg", "pdf"],
        "seqdiag": ["png", "svg", "pdf"],
        "actdiag": ["png", "svg", "pdf"],
        "nwdiag": ["png", "svg", "pdf"],
        "packetdiag": ["png", "svg", "pdf"],
        "rackdiag": ["png", "svg", "pdf"],
    }

    kroki_bpmn: ClassVar[dict[str, list[str]]] = {
        "bpmn": ["svg"],
    }

    kroki_excalidraw: ClassVar[dict[str, list[str]]] = {
        "excalidraw": ["svg"],
    }

    kroki_mermaid: ClassVar[dict[str, list[str]]] = {
        "mermaid": ["png", "svg"],
    }

    kroki_diagramsnet: ClassVar[dict[str, list[str]]] = {
        "diagramsnet": ["svg"],
    }

    def __init__(
        self,
        *,
        blockdiag_enabled: bool,
        bpmn_enabled: bool,
        excalidraw_enabled: bool,
        mermaid_enabled: bool,
        diagramsnet_enabled: bool,
        file_types: list[str],
        file_type_overrides: dict[str, str],
    ):
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
                    filter(lambda file: file in diagram_file_types, file_types), None
                )

        for diagram_type, diagram_file_type in file_type_overrides.items():
            self.diagram_types_supporting_file[diagram_type] = diagram_file_type

        log.debug("File and Diagram types configured: %s", self.diagram_types_supporting_file)

    def get_file_ext(self, kroki_type: str) -> str:
        return self.diagram_types_supporting_file[kroki_type]
