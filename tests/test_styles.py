import json
import textwrap
from unittest.mock import MagicMock

import pytest

from kroki.parsing import MarkdownParser
from kroki.styles import StyleInjector

FULL_STYLES = {
    "box": {"fill": "#e6f3ff", "stroke": "#0066cc"},
    "text": {"fill": "#333", "font-family": "Arial", "font-size": "14"},
    "line": {"stroke": "#666"},
    "background": {"fill": "#fff"},
}


def _parse_mermaid_init(line: str) -> dict:
    """Parse %%{init: {...}}%% into the JSON payload."""
    assert line.startswith("%%{init: ") and line.endswith("}%%")
    json_str = line[len("%%{init: ") : -len("}%%")]
    return json.loads(json_str)


# --- PlantUML ---


def test_plantuml_full_config() -> None:
    injector = StyleInjector(FULL_STYLES)
    source = "@startuml\nAlice -> Bob\n@enduml"
    result = injector.inject("plantuml", source)
    assert "skinparam RectangleBackgroundColor #e6f3ff" in result
    assert "skinparam RectangleBorderColor #0066cc" in result
    assert "skinparam defaultFontColor #333" in result
    assert "skinparam defaultFontName Arial" in result
    assert "skinparam defaultFontSize 14" in result
    assert "skinparam ArrowColor #666" in result
    assert "skinparam BackgroundColor #fff" in result


def test_plantuml_directives_after_startuml() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = "@startuml\nAlice -> Bob\n@enduml"
    result = injector.inject("plantuml", source)
    lines = result.split("\n")
    assert lines[0] == "@startuml"
    assert "skinparam RectangleBackgroundColor #e6f3ff" in lines[1]


def test_plantuml_directives_after_startmindmap() -> None:
    injector = StyleInjector({"background": {"fill": "#fff"}})
    source = "@startmindmap\n* root\n@endmindmap"
    result = injector.inject("plantuml", source)
    lines = result.split("\n")
    assert lines[0] == "@startmindmap"
    assert "skinparam BackgroundColor #fff" in lines[1]


def test_plantuml_does_not_use_update_element_style() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = "@startuml\nAlice -> Bob\n@enduml"
    result = injector.inject("plantuml", source)
    assert "UpdateElementStyle" not in result


def test_plantuml_partial_config() -> None:
    injector = StyleInjector({"text": {"fill": "#333"}})
    source = "@startuml\nAlice -> Bob\n@enduml"
    result = injector.inject("plantuml", source)
    assert "skinparam defaultFontColor #333" in result
    assert "BackgroundColor" not in result.replace("skinparam defaultFontColor", "")
    assert "BorderColor" not in result


def test_plantuml_text_color_alias() -> None:
    injector = StyleInjector({"text": {"color": "#333"}})
    source = "@startuml\nAlice -> Bob\n@enduml"
    result = injector.inject("plantuml", source)
    assert "skinparam defaultFontColor #333" in result


def test_plantuml_text_fill_takes_precedence_over_color() -> None:
    injector = StyleInjector({"text": {"fill": "#111", "color": "#222"}})
    source = "@startuml\nAlice -> Bob\n@enduml"
    result = injector.inject("plantuml", source)
    assert "skinparam defaultFontColor #111" in result
    assert "#222" not in result


def test_plantuml_actor_styling() -> None:
    injector = StyleInjector({"actor": {"fill": "#ffe0b2", "stroke": "#bf360c"}})
    source = "@startuml\nactor User\n@enduml"
    result = injector.inject("plantuml", source)
    assert "skinparam ActorBackgroundColor #ffe0b2" in result
    assert "skinparam ActorBorderColor #bf360c" in result


def test_plantuml_actor_independent_from_box() -> None:
    injector = StyleInjector(
        {
            "box": {"fill": "#e6f3ff"},
            "actor": {"fill": "#ffe0b2"},
        }
    )
    source = "@startuml\nactor User\n@enduml"
    result = injector.inject("plantuml", source)
    assert "skinparam ActorBackgroundColor #ffe0b2" in result
    assert "skinparam RectangleBackgroundColor #e6f3ff" in result


# --- C4 PlantUML ---


def test_c4plantuml_full_config() -> None:
    injector = StyleInjector(FULL_STYLES)
    source = '@startuml\n!include <C4/C4_Context>\nPerson(user, "User")\n@enduml'
    result = injector.inject("c4plantuml", source)
    assert (
        'UpdateElementStyle("system", $bgColor="#e6f3ff", $borderColor="#0066cc", $fontColor="#333")'
        in result
    )
    assert (
        'UpdateElementStyle("person", $bgColor="#e6f3ff", $borderColor="#0066cc", $fontColor="#333")'
        in result
    )
    assert "skinparam defaultFontColor #333" in result
    assert "skinparam defaultFontName Arial" in result
    assert "skinparam ArrowColor #666" in result
    assert "skinparam BackgroundColor #fff" in result


def test_c4plantuml_actor_overrides_person_elements() -> None:
    styles = {**FULL_STYLES, "actor": {"fill": "#ffe0b2", "stroke": "#bf360c"}}
    injector = StyleInjector(styles)
    source = "@startuml\n!include <C4/C4_Context>\n@enduml"
    result = injector.inject("c4plantuml", source)
    assert (
        'UpdateElementStyle("person", $bgColor="#ffe0b2", $borderColor="#bf360c", $fontColor="#333")'
        in result
    )
    assert (
        'UpdateElementStyle("external_person", $bgColor="#ffe0b2", $borderColor="#bf360c", $fontColor="#333")'
        in result
    )
    assert (
        'UpdateElementStyle("system", $bgColor="#e6f3ff", $borderColor="#0066cc", $fontColor="#333")'
        in result
    )


def test_c4plantuml_element_styles_after_last_include() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = '@startuml\n!include <C4/C4_Context>\n!include <C4/C4_Container>\nPerson(user, "User")\n@enduml'
    result = injector.inject("c4plantuml", source)
    lines = result.split("\n")
    last_include_idx = max(
        i for i, line in enumerate(lines) if line.startswith("!include")
    )
    update_idx = next(i for i, line in enumerate(lines) if "UpdateElementStyle" in line)
    assert update_idx == last_include_idx + 1


def test_c4plantuml_skinparams_after_startuml() -> None:
    injector = StyleInjector({"background": {"fill": "#fff"}})
    source = '@startuml\n!include <C4/C4_Context>\nPerson(user, "User")\n@enduml'
    result = injector.inject("c4plantuml", source)
    lines = result.split("\n")
    assert lines[0] == "@startuml"
    assert "skinparam BackgroundColor #fff" in lines[1]


def test_c4plantuml_all_element_types_styled() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = "@startuml\n!include <C4/C4_Context>\n@enduml"
    result = injector.inject("c4plantuml", source)
    for elem in (
        "person",
        "external_person",
        "system",
        "external_system",
        "container",
        "external_container",
        "component",
        "external_component",
        "node",
    ):
        assert f'UpdateElementStyle("{elem}"' in result


def test_c4plantuml_no_includes_falls_back_to_start_marker() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = '@startuml\nPerson(user, "User")\n@enduml'
    result = injector.inject("c4plantuml", source)
    assert 'UpdateElementStyle("person"' in result
    lines = result.split("\n")
    assert lines[0] == "@startuml"


def test_c4plantuml_partial_config_only_box() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = "@startuml\n!include <C4/C4_Context>\n@enduml"
    result = injector.inject("c4plantuml", source)
    assert 'UpdateElementStyle("person", $bgColor="#e6f3ff")' in result
    assert "skinparam" not in result


# --- Mermaid ---


def test_mermaid_full_config() -> None:
    injector = StyleInjector(FULL_STYLES)
    source = "graph TD\n  A-->B"
    result = injector.inject("mermaid", source)
    init_line = result.split("\n")[0]
    parsed = _parse_mermaid_init(init_line)
    assert parsed["theme"] == "base"
    tv = parsed["themeVariables"]
    assert tv["primaryColor"] == "#e6f3ff"
    assert tv["primaryBorderColor"] == "#0066cc"
    assert tv["primaryTextColor"] == "#333"
    assert tv["lineColor"] == "#666"
    assert tv["background"] == "#fff"


def test_mermaid_partial_config() -> None:
    injector = StyleInjector({"line": {"stroke": "#666"}})
    source = "graph TD\n  A-->B"
    result = injector.inject("mermaid", source)
    init_line = result.split("\n")[0]
    parsed = _parse_mermaid_init(init_line)
    assert parsed["theme"] == "base"
    assert parsed["themeVariables"] == {"lineColor": "#666"}


def test_mermaid_text_color_alias() -> None:
    injector = StyleInjector({"text": {"color": "#333"}})
    source = "graph TD\n  A-->B"
    result = injector.inject("mermaid", source)
    init_line = result.split("\n")[0]
    parsed = _parse_mermaid_init(init_line)
    assert parsed["themeVariables"]["primaryTextColor"] == "#333"


def test_mermaid_actor_styling() -> None:
    injector = StyleInjector(
        {"actor": {"fill": "#ffe0b2", "stroke": "#bf360c", "color": "#333"}}
    )
    source = "sequenceDiagram\n  Alice->>Bob: Hello"
    result = injector.inject("mermaid", source)
    init_line = result.split("\n")[0]
    parsed = _parse_mermaid_init(init_line)
    tv = parsed["themeVariables"]
    assert tv["actorBkg"] == "#ffe0b2"
    assert tv["actorBorder"] == "#bf360c"
    assert tv["actorTextColor"] == "#333"
    assert tv["mainContrastColor"] == "#333"


# --- GraphViz ---


def test_graphviz_full_config() -> None:
    injector = StyleInjector(FULL_STYLES)
    source = "digraph G {\n  A -> B;\n}"
    result = injector.inject("graphviz", source)
    assert 'fillcolor="#e6f3ff"' in result
    assert 'style="filled"' in result
    assert 'color="#0066cc"' in result
    assert 'fontcolor="#333"' in result
    assert 'fontname="Arial"' in result
    assert 'edge [color="#666"]' in result
    assert 'bgcolor="#fff"' in result


def test_graphviz_attributes_after_opening_brace() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = "digraph G {\n  A -> B;\n}"
    result = injector.inject("graphviz", source)
    brace_pos = result.index("{")
    after_brace = result[brace_pos + 1 :]
    assert after_brace.startswith("\nnode [")


def test_graphviz_source_without_opening_brace() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = "no brace here"
    result = injector.inject("graphviz", source)
    assert result == source


def test_graphviz_partial_config() -> None:
    injector = StyleInjector({"line": {"stroke": "#666"}})
    source = "digraph G {\n  A -> B;\n}"
    result = injector.inject("graphviz", source)
    assert 'edge [color="#666"]' in result
    assert "node [" not in result


def test_graphviz_text_color_alias() -> None:
    injector = StyleInjector({"text": {"color": "#333"}})
    source = "digraph G {\n  A -> B;\n}"
    result = injector.inject("graphviz", source)
    assert 'fontcolor="#333"' in result


def test_graphviz_line_font_color() -> None:
    injector = StyleInjector({"line": {"stroke": "#666", "font-color": "#999"}})
    source = "digraph G {\n  A -> B;\n}"
    result = injector.inject("graphviz", source)
    assert 'edge [color="#666", fontcolor="#999"]' in result


def test_graphviz_line_font_family() -> None:
    injector = StyleInjector({"line": {"font-family": "Courier"}})
    source = "digraph G {\n  A -> B;\n}"
    result = injector.inject("graphviz", source)
    assert 'edge [fontname="Courier"]' in result


# --- BlockDiag ---


def test_blockdiag_full_config() -> None:
    injector = StyleInjector(FULL_STYLES)
    source = "blockdiag {\n  A -> B;\n}"
    result = injector.inject("blockdiag", source)
    assert 'default_node_color = "#e6f3ff"' in result
    assert 'default_textcolor = "#333"' in result
    assert "default_fontsize = 14" in result
    assert 'default_linecolor = "#666"' in result


def test_blockdiag_attributes_after_opening_brace() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = "blockdiag {\n  A -> B;\n}"
    result = injector.inject("blockdiag", source)
    brace_pos = result.index("{")
    after_brace = result[brace_pos + 1 :]
    assert after_brace.startswith('\ndefault_node_color = "#e6f3ff"')


@pytest.mark.parametrize(
    "diagram_type",
    ["blockdiag", "seqdiag", "actdiag", "nwdiag", "packetdiag", "rackdiag"],
)
def test_all_blockdiag_types_use_same_handler(diagram_type: str) -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = f"{diagram_type} {{\n  A -> B;\n}}"
    result = injector.inject(diagram_type, source)
    assert 'default_node_color = "#e6f3ff"' in result


def test_blockdiag_text_color_alias() -> None:
    injector = StyleInjector({"text": {"color": "#333"}})
    source = "blockdiag {\n  A -> B;\n}"
    result = injector.inject("blockdiag", source)
    assert 'default_textcolor = "#333"' in result


# --- Nomnoml ---


def test_nomnoml_full_config() -> None:
    injector = StyleInjector(FULL_STYLES)
    source = "[A] -> [B]"
    result = injector.inject("nomnoml", source)
    assert "#fill: #e6f3ff" in result
    assert "#stroke: #0066cc" in result
    assert "#background: #fff" in result
    assert "#font: Arial" in result
    assert "#fontSize: 14" in result


def test_nomnoml_directives_prepended() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = "[A] -> [B]"
    result = injector.inject("nomnoml", source)
    lines = result.split("\n")
    assert lines[0] == "#fill: #e6f3ff"
    assert lines[1] == "[A] -> [B]"


# --- D2 ---


def test_d2_full_config() -> None:
    injector = StyleInjector(FULL_STYLES)
    source = "x -> y"
    result = injector.inject("d2", source)
    assert '**.style.fill: "#e6f3ff"' in result
    assert '**.style.stroke: "#0066cc"' in result
    assert '**.style.font-color: "#333"' in result
    assert "**.style.font-size: 14" in result
    assert '(** -> **)[*].style.stroke: "#666"' in result
    assert 'style.fill: "#fff"' in result


def test_d2_directives_prepended() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = "x -> y"
    result = injector.inject("d2", source)
    lines = result.split("\n")
    assert lines[0] == '**.style.fill: "#e6f3ff"'
    assert lines[-1] == "x -> y"


def test_d2_partial_config() -> None:
    injector = StyleInjector({"line": {"stroke": "#666"}})
    source = "x -> y"
    result = injector.inject("d2", source)
    assert '(** -> **)[*].style.stroke: "#666"' in result
    assert "**.style.fill" not in result


def test_d2_text_color_alias() -> None:
    injector = StyleInjector({"text": {"color": "#333"}})
    source = "x -> y"
    result = injector.inject("d2", source)
    assert '**.style.font-color: "#333"' in result


def test_d2_line_font_color() -> None:
    injector = StyleInjector({"line": {"stroke": "#666", "font-color": "#999"}})
    source = "x -> y"
    result = injector.inject("d2", source)
    assert '(** -> **)[*].style.stroke: "#666"' in result
    assert '(** -> **)[*].style.font-color: "#999"' in result


# --- Structurizr ---


def test_structurizr_full_config() -> None:
    injector = StyleInjector(FULL_STYLES)
    source = textwrap.dedent("""\
        workspace {
          model {
            user = person "User"
          }
          views {
            systemContext user {
              include *
            }
          }
        }""")
    result = injector.inject("structurizr", source)
    assert "background #e6f3ff" in result
    assert "stroke #0066cc" in result
    assert "color #333" in result
    assert "fontSize 14" in result
    assert 'element "Element"' in result
    assert 'relationship "Relationship"' in result


def test_structurizr_injects_into_existing_styles_block() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = textwrap.dedent("""\
        workspace {
          views {
            styles {
            }
          }
        }""")
    result = injector.inject("structurizr", source)
    assert 'element "Element"' in result
    assert "background #e6f3ff" in result


def test_structurizr_creates_styles_block_inside_views() -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    source = textwrap.dedent("""\
        workspace {
          model {
            user = person "User"
          }
          views {
            systemContext user {
              include *
            }
          }
        }""")
    result = injector.inject("structurizr", source)
    assert "styles {" in result
    assert "background #e6f3ff" in result


def test_structurizr_partial_config_line_only() -> None:
    injector = StyleInjector({"line": {"stroke": "#666"}})
    source = textwrap.dedent("""\
        workspace {
          views {
          }
        }""")
    result = injector.inject("structurizr", source)
    assert 'relationship "Relationship"' in result
    assert "color #666" in result
    assert 'element "Element"' not in result


def test_structurizr_actor_creates_person_element() -> None:
    injector = StyleInjector({"actor": {"fill": "#ffe0b2", "stroke": "#bf360c"}})
    source = textwrap.dedent("""\
        workspace {
          views {
          }
        }""")
    result = injector.inject("structurizr", source)
    assert 'element "Person"' in result
    assert "background #ffe0b2" in result
    assert "stroke #bf360c" in result


# --- General ---


def test_empty_styles_returns_source_unchanged() -> None:
    injector = StyleInjector({})
    source = "@startuml\nAlice -> Bob\n@enduml"
    assert injector.inject("plantuml", source) == source


@pytest.mark.parametrize(
    "diagram_type",
    ["svgbob", "ditaa", "excalidraw", "bpmn", "erd", "pikchr", "vega"],
)
def test_unsupported_diagram_type_returns_source_unchanged(diagram_type: str) -> None:
    injector = StyleInjector(FULL_STYLES)
    source = "some diagram source"
    assert injector.inject(diagram_type, source) == source


# --- Integration (via MarkdownParser) ---


def test_no_style_inject_skips_injection(mock_kroki_diagram_types, kroki_dummy) -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    parser = MarkdownParser("/tmp", mock_kroki_diagram_types, style_injector=injector)
    md = textwrap.dedent("""\
        ```plantuml no-style-inject=true
        @startuml
        Alice -> Bob
        @enduml
        ```
    """)
    captured_data = []

    async def capture_callback(kroki_context, mkdocs_context):
        captured_data.append(kroki_context.data.unwrap())
        return "<img />"

    ctx = MagicMock()
    parser.replace_kroki_blocks(md, capture_callback, ctx)
    assert len(captured_data) == 1
    assert "skinparam" not in captured_data[0]


def test_styles_are_injected_when_configured(
    mock_kroki_diagram_types, kroki_dummy
) -> None:
    injector = StyleInjector({"box": {"fill": "#e6f3ff"}})
    parser = MarkdownParser("/tmp", mock_kroki_diagram_types, style_injector=injector)
    md = textwrap.dedent("""\
        ```plantuml
        @startuml
        Alice -> Bob
        @enduml
        ```
    """)
    captured_data = []

    async def capture_callback(kroki_context, mkdocs_context):
        captured_data.append(kroki_context.data.unwrap())
        return "<img />"

    ctx = MagicMock()
    parser.replace_kroki_blocks(md, capture_callback, ctx)
    assert len(captured_data) == 1
    assert "skinparam RectangleBackgroundColor #e6f3ff" in captured_data[0]


def test_no_style_injector_leaves_source_unchanged(
    mock_kroki_diagram_types, kroki_dummy
) -> None:
    parser = MarkdownParser("/tmp", mock_kroki_diagram_types)
    md = textwrap.dedent("""\
        ```plantuml
        @startuml
        Alice -> Bob
        @enduml
        ```
    """)
    captured_data = []

    async def capture_callback(kroki_context, mkdocs_context):
        captured_data.append(kroki_context.data.unwrap())
        return "<img />"

    ctx = MagicMock()
    parser.replace_kroki_blocks(md, capture_callback, ctx)
    assert len(captured_data) == 1
    assert captured_data[0] == "@startuml\nAlice -> Bob\n@enduml\n"
