from collections import ChainMap
from typing import ClassVar

from kroki.logging import log


class KrokiDiagramTypes:
    _kroki_base: ClassVar[dict[str, list[str]]] = {
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

    _kroki_blockdiag: ClassVar[dict[str, list[str]]] = {
        "blockdiag": ["png", "svg", "pdf"],
        "seqdiag": ["png", "svg", "pdf"],
        "actdiag": ["png", "svg", "pdf"],
        "nwdiag": ["png", "svg", "pdf"],
        "packetdiag": ["png", "svg", "pdf"],
        "rackdiag": ["png", "svg", "pdf"],
    }

    _kroki_bpmn: ClassVar[dict[str, list[str]]] = {
        "bpmn": ["svg"],
    }

    _kroki_excalidraw: ClassVar[dict[str, list[str]]] = {
        "excalidraw": ["svg"],
    }

    _kroki_mermaid: ClassVar[dict[str, list[str]]] = {
        "mermaid": ["png", "svg"],
    }

    _kroki_diagramsnet: ClassVar[dict[str, list[str]]] = {
        "diagramsnet": ["svg"],
    }

    def __init__(
        self,
        fence_prefix: str,
        file_types: list[str],
        file_type_overrides: dict[str, str],
        *,
        blockdiag_enabled: bool,
        bpmn_enabled: bool,
        excalidraw_enabled: bool,
        mermaid_enabled: bool,
        diagramsnet_enabled: bool,
    ):
        self._fence_prefix = fence_prefix

        kroki_types = ChainMap(
            self._kroki_base,
            self._kroki_blockdiag if blockdiag_enabled else {},
            self._kroki_bpmn if bpmn_enabled else {},
            self._kroki_excalidraw if excalidraw_enabled else {},
            self._kroki_mermaid if mermaid_enabled else {},
            self._kroki_diagramsnet if diagramsnet_enabled else {},
        )

        self._kroki_types_supporting_file = {}

        for kroki_type, kroki_file_types in kroki_types.items():
            kroki_file_type = next(filter(lambda file: file in kroki_file_types, file_types), None)
            if kroki_file_type is not None:
                self._kroki_types_supporting_file[kroki_type] = next(
                    filter(lambda file: file in kroki_file_types, file_types), None
                )

        for kroki_type, kroki_file_type in file_type_overrides.items():
            self._kroki_types_supporting_file[kroki_type] = kroki_file_type

        log.debug("File and Diagram types configured: %s", self._kroki_types_supporting_file)

    def get_file_ext(self, kroki_type: str) -> str:
        return self._kroki_types_supporting_file[kroki_type]

    def get_kroki_type(self, block_type: None | str) -> None | str:
        if block_type is None:
            return
        if not block_type.startswith(self._fence_prefix):
            return
        kroki_type = block_type.removeprefix(self._fence_prefix).lower()
        if kroki_type not in self._kroki_types_supporting_file:
            return

        return kroki_type
