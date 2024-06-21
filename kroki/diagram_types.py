from collections import ChainMap
from typing import ClassVar

from mkdocs.exceptions import PluginError

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

        diagram_type_file_ext_map = ChainMap(
            self._kroki_base,
            self._kroki_blockdiag if blockdiag_enabled else {},
            self._kroki_bpmn if bpmn_enabled else {},
            self._kroki_excalidraw if excalidraw_enabled else {},
            self._kroki_mermaid if mermaid_enabled else {},
            self._kroki_diagramsnet if diagramsnet_enabled else {},
        )

        self._kroki_type_file_ext_mapping: dict[str, str] = self._get_kroki_type_file_ext_mapping(
            diagram_type_file_ext_map, file_types, file_type_overrides
        )

        log.debug("File and Diagram types configured: %s", self._kroki_type_file_ext_mapping)

    def _get_kroki_type_file_ext_mapping(
        self,
        diagram_type_file_ext_map: ChainMap[str, list[str]],
        file_types: list[str],
        file_type_overrides: dict[str, str],
    ) -> dict[str, str]:
        def get_file_type(kroki_type: str) -> str:
            supported_file_types = diagram_type_file_ext_map[kroki_type]
            file_type_override = file_type_overrides.get(kroki_type)
            if file_type_override is not None:
                if file_type_override not in supported_file_types:
                    err_msg = (
                        f"{kroki_type}: {file_type_override} not in supported file types: " f"{supported_file_types}"
                    )
                    raise PluginError(err_msg)
                return file_type_override

            try:
                target_file_type = next(t for t in file_types if t in supported_file_types)
            except StopIteration as e:
                err_msg = (
                    f"{kroki_type}: Not able to satisfy any of {file_types}, "
                    f"supported file types: {supported_file_types}"
                )
                raise PluginError(err_msg) from e
            else:
                return target_file_type

        return {kroki_type: get_file_type(kroki_type) for kroki_type in diagram_type_file_ext_map}

    def get_file_ext(self, kroki_type: str) -> str:
        return self._kroki_type_file_ext_mapping[kroki_type]

    def get_kroki_type(self, block_type: None | str) -> str | None:
        if block_type is None:
            return None
        if not block_type.startswith(self._fence_prefix):
            return None
        kroki_type = block_type.removeprefix(self._fence_prefix).lower()
        if kroki_type not in self._kroki_type_file_ext_mapping:
            return None

        return kroki_type
