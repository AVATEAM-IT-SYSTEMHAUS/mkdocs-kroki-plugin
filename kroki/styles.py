from __future__ import annotations

import json
import re

from kroki.logging import log

_BLOCKDIAG_TYPES = frozenset(
    {"blockdiag", "seqdiag", "actdiag", "nwdiag", "packetdiag", "rackdiag"}
)

_C4_PERSON_TYPES = ("person", "external_person")

_C4_BOX_TYPES = (
    "system",
    "external_system",
    "container",
    "external_container",
    "component",
    "external_component",
    "node",
)

_PLANTUML_SKINPARAM_ELEMENTS = (
    "Rectangle",
    "Component",
    "Class",
    "Object",
    "Activity",
    "State",
    "Usecase",
    "Sequence",
    "Participant",
    "Entity",
    "Database",
    "Collections",
    "Queue",
    "Node",
    "Card",
    "Package",
)


class StyleInjector:
    """Translates generic style config into diagram-type-specific directives."""

    def __init__(self, styles: dict) -> None:
        self._styles = styles

    def inject(self, diagram_type: str, source: str) -> str:
        if diagram_type == "c4plantuml":
            return self._inject_c4plantuml(source)
        if diagram_type == "plantuml":
            return self._inject_plantuml(source)
        if diagram_type == "mermaid":
            return self._inject_mermaid(source)
        if diagram_type == "graphviz":
            return self._inject_graphviz(source)
        if diagram_type in _BLOCKDIAG_TYPES:
            return self._inject_blockdiag(source)
        if diagram_type == "nomnoml":
            return self._inject_nomnoml(source)
        if diagram_type == "d2":
            return self._inject_d2(source)
        if diagram_type == "structurizr":
            return self._inject_structurizr(source)

        log.debug("Style injection not supported for diagram type: %s", diagram_type)
        return source

    def _inject_plantuml(self, source: str) -> str:
        lines: list[str] = []
        box = self._styles.get("box", {})
        actor = self._styles.get("actor", {})
        text = self._styles.get("text", {})
        line = self._styles.get("line", {})
        background = self._styles.get("background", {})

        if box_fill := box.get("fill"):
            for elem in _PLANTUML_SKINPARAM_ELEMENTS:
                lines.append(f"skinparam {elem}BackgroundColor {box_fill}")
        if box_stroke := box.get("stroke"):
            for elem in _PLANTUML_SKINPARAM_ELEMENTS:
                lines.append(f"skinparam {elem}BorderColor {box_stroke}")

        if actor_fill := actor.get("fill"):
            lines.append(f"skinparam ActorBackgroundColor {actor_fill}")
        if actor_stroke := actor.get("stroke"):
            lines.append(f"skinparam ActorBorderColor {actor_stroke}")

        text_color = text.get("fill") or text.get("color")
        if text_color:
            lines.append(f"skinparam defaultFontColor {text_color}")
        if text_font := text.get("font-family"):
            lines.append(f"skinparam defaultFontName {text_font}")
        if text_size := text.get("font-size"):
            lines.append(f"skinparam defaultFontSize {text_size}")

        if line_stroke := line.get("stroke"):
            lines.append(f"skinparam ArrowColor {line_stroke}")

        note = self._styles.get("note", {})
        if note_fill := note.get("fill"):
            lines.append(f"skinparam NoteBackgroundColor {note_fill}")
        if note_stroke := note.get("stroke"):
            lines.append(f"skinparam NoteBorderColor {note_stroke}")
        if note_color := note.get("color"):
            lines.append(f"skinparam NoteFontColor {note_color}")

        package = self._styles.get("package", {})
        if package_fill := package.get("fill"):
            lines.append(f"skinparam PackageBackgroundColor {package_fill}")
        if package_stroke := package.get("stroke"):
            lines.append(f"skinparam PackageBorderColor {package_stroke}")
        if package_color := package.get("color"):
            lines.append(f"skinparam PackageFontColor {package_color}")

        if bg_fill := background.get("fill"):
            lines.append(f"skinparam BackgroundColor {bg_fill}")

        if not lines:
            return source

        directives = "\n".join(lines)
        return self._inject_after_start_marker(source, directives)

    def _inject_c4plantuml(self, source: str) -> str:
        skinparams: list[str] = []
        element_styles: list[str] = []
        box = self._styles.get("box", {})
        actor = self._styles.get("actor", {})
        text = self._styles.get("text", {})
        line = self._styles.get("line", {})
        background = self._styles.get("background", {})

        text_color = text.get("fill") or text.get("color")

        # Build UpdateElementStyle args for box elements
        box_args: list[str] = []
        if box_fill := box.get("fill"):
            box_args.append(f'$bgColor="{box_fill}"')
        if box_stroke := box.get("stroke"):
            box_args.append(f'$borderColor="{box_stroke}"')
        if text_color:
            box_args.append(f'$fontColor="{text_color}"')
        if box_args:
            args_str = ", ".join(box_args)
            for elem in _C4_BOX_TYPES:
                element_styles.append(f'UpdateElementStyle("{elem}", {args_str})')

        # Build UpdateElementStyle args for person/actor elements
        actor_args: list[str] = []
        if actor_fill := actor.get("fill"):
            actor_args.append(f'$bgColor="{actor_fill}"')
        elif box_fill:
            actor_args.append(f'$bgColor="{box_fill}"')
        if actor_stroke := actor.get("stroke"):
            actor_args.append(f'$borderColor="{actor_stroke}"')
        elif box_stroke:
            actor_args.append(f'$borderColor="{box_stroke}"')
        if text_color:
            actor_args.append(f'$fontColor="{text_color}"')
        if actor_args:
            args_str = ", ".join(actor_args)
            for elem in _C4_PERSON_TYPES:
                element_styles.append(f'UpdateElementStyle("{elem}", {args_str})')

        # General skinparams for text, arrows, background
        if text_color:
            skinparams.append(f"skinparam defaultFontColor {text_color}")
        if text_font := text.get("font-family"):
            skinparams.append(f"skinparam defaultFontName {text_font}")
        if text_size := text.get("font-size"):
            skinparams.append(f"skinparam defaultFontSize {text_size}")
        if line_stroke := line.get("stroke"):
            skinparams.append(f"skinparam ArrowColor {line_stroke}")

        note = self._styles.get("note", {})
        if note_fill := note.get("fill"):
            skinparams.append(f"skinparam NoteBackgroundColor {note_fill}")
        if note_stroke := note.get("stroke"):
            skinparams.append(f"skinparam NoteBorderColor {note_stroke}")
        if note_color := note.get("color"):
            skinparams.append(f"skinparam NoteFontColor {note_color}")

        package = self._styles.get("package", {})
        if package_fill := package.get("fill"):
            skinparams.append(f"skinparam PackageBackgroundColor {package_fill}")
        if package_stroke := package.get("stroke"):
            skinparams.append(f"skinparam PackageBorderColor {package_stroke}")
        if package_color := package.get("color"):
            skinparams.append(f"skinparam PackageFontColor {package_color}")

        if bg_fill := background.get("fill"):
            skinparams.append(f"skinparam BackgroundColor {bg_fill}")

        if not skinparams and not element_styles:
            return source

        # Skinparams go after @startuml
        if skinparams:
            source = self._inject_after_start_marker(source, "\n".join(skinparams))

        # UpdateElementStyle calls must go after !include directives
        if element_styles:
            source = self._inject_after_last_include(source, "\n".join(element_styles))

        return source

    @staticmethod
    def _inject_after_last_include(source: str, directives: str) -> str:
        """Insert directives after the last !include line in the source."""
        last_include = None
        for match in re.finditer(r"^!include\s+.*$", source, re.MULTILINE):
            last_include = match
        if last_include:
            insert_pos = last_include.end()
            return source[:insert_pos] + "\n" + directives + source[insert_pos:]
        # No includes found, fall back to after @startXXX
        return StyleInjector._inject_after_start_marker(source, directives)

    @staticmethod
    def _inject_after_start_marker(source: str, directives: str) -> str:
        """Insert directives after @startXXX line in PlantUML source."""
        match = re.search(r"^(@start\w+.*)$", source, re.MULTILINE)
        if match:
            insert_pos = match.end()
            return source[:insert_pos] + "\n" + directives + source[insert_pos:]
        return directives + "\n" + source

    def _inject_mermaid(self, source: str) -> str:
        theme_vars: dict[str, str] = {}
        box = self._styles.get("box", {})
        actor = self._styles.get("actor", {})
        text = self._styles.get("text", {})
        line = self._styles.get("line", {})
        background = self._styles.get("background", {})

        if box_fill := box.get("fill"):
            theme_vars["primaryColor"] = box_fill
        if box_stroke := box.get("stroke"):
            theme_vars["primaryBorderColor"] = box_stroke

        if actor_fill := actor.get("fill"):
            theme_vars["actorBkg"] = actor_fill
        if actor_stroke := actor.get("stroke"):
            theme_vars["actorBorder"] = actor_stroke

        text_color = text.get("fill") or text.get("color")
        if text_color:
            theme_vars["primaryTextColor"] = text_color

        actor_text_color = actor.get("color") or text_color
        if actor_text_color:
            theme_vars["actorTextColor"] = actor_text_color
            theme_vars["mainContrastColor"] = actor_text_color

        if line_stroke := line.get("stroke"):
            theme_vars["lineColor"] = line_stroke
        if line_label_bg := line.get("label-background"):
            theme_vars["edgeLabelBackground"] = line_label_bg

        note = self._styles.get("note", {})
        if note_fill := note.get("fill"):
            theme_vars["noteBkgColor"] = note_fill
        if note_stroke := note.get("stroke"):
            theme_vars["noteBorderColor"] = note_stroke
        if note_color := note.get("color"):
            theme_vars["noteTextColor"] = note_color

        if bg_fill := background.get("fill"):
            theme_vars["background"] = bg_fill

        if not theme_vars:
            return source

        init_payload = json.dumps({"theme": "base", "themeVariables": theme_vars})
        return f"%%{{init: {init_payload}}}%%\n{source}"

    def _inject_graphviz(self, source: str) -> str:
        attrs: list[str] = []
        box = self._styles.get("box", {})
        text = self._styles.get("text", {})
        line = self._styles.get("line", {})
        background = self._styles.get("background", {})

        node_attrs: list[str] = []
        if box_fill := box.get("fill"):
            node_attrs.append(f'fillcolor="{box_fill}"')
            node_attrs.append('style="filled"')
        if box_stroke := box.get("stroke"):
            node_attrs.append(f'color="{box_stroke}"')

        text_color = text.get("fill") or text.get("color")
        if text_color:
            node_attrs.append(f'fontcolor="{text_color}"')
        if text_font := text.get("font-family"):
            node_attrs.append(f'fontname="{text_font}"')

        if node_attrs:
            attrs.append(f"node [{', '.join(node_attrs)}];")

        edge_attrs: list[str] = []
        if line_stroke := line.get("stroke"):
            edge_attrs.append(f'color="{line_stroke}"')
        line_font_color = line.get("font-color") or line.get("font_color")
        if line_font_color:
            edge_attrs.append(f'fontcolor="{line_font_color}"')
        if line_font := line.get("font-family"):
            edge_attrs.append(f'fontname="{line_font}"')
        if edge_attrs:
            attrs.append(f"edge [{', '.join(edge_attrs)}];")

        graph_attrs: list[str] = []
        if bg_fill := background.get("fill"):
            graph_attrs.append(f'bgcolor="{bg_fill}"')
        if graph_attrs:
            attrs.append(f"graph [{', '.join(graph_attrs)}];")

        if not attrs:
            return source

        directives = "\n".join(attrs)
        return self._inject_after_opening_brace(source, directives)

    def _inject_blockdiag(self, source: str) -> str:
        lines: list[str] = []
        box = self._styles.get("box", {})
        text = self._styles.get("text", {})
        line = self._styles.get("line", {})

        if box_fill := box.get("fill"):
            lines.append(f'default_node_color = "{box_fill}";')

        text_color = text.get("fill") or text.get("color")
        if text_color:
            lines.append(f'default_textcolor = "{text_color}";')
        if text_size := text.get("font-size"):
            lines.append(f"default_fontsize = {text_size};")

        if line_stroke := line.get("stroke"):
            lines.append(f'default_linecolor = "{line_stroke}";')

        if not lines:
            return source

        directives = "\n".join(lines)
        return self._inject_after_opening_brace(source, directives)

    def _inject_nomnoml(self, source: str) -> str:
        lines: list[str] = []
        box = self._styles.get("box", {})
        text = self._styles.get("text", {})
        background = self._styles.get("background", {})

        if box_fill := box.get("fill"):
            lines.append(f"#fill: {box_fill}")
        if box_stroke := box.get("stroke"):
            lines.append(f"#stroke: {box_stroke}")

        if bg_fill := background.get("fill"):
            lines.append(f"#background: {bg_fill}")

        if text_font := text.get("font-family"):
            lines.append(f"#font: {text_font}")
        if text_size := text.get("font-size"):
            lines.append(f"#fontSize: {text_size}")

        if not lines:
            return source

        directives = "\n".join(lines)
        return f"{directives}\n{source}"

    def _inject_d2(self, source: str) -> str:
        lines: list[str] = []
        box = self._styles.get("box", {})
        text = self._styles.get("text", {})
        line = self._styles.get("line", {})
        background = self._styles.get("background", {})

        if box_fill := box.get("fill"):
            lines.append(f'**.style.fill: "{box_fill}"')
        if box_stroke := box.get("stroke"):
            lines.append(f'**.style.stroke: "{box_stroke}"')

        text_color = text.get("fill") or text.get("color")
        if text_color:
            lines.append(f'**.style.font-color: "{text_color}"')
        if text_size := text.get("font-size"):
            lines.append(f"**.style.font-size: {text_size}")

        if line_stroke := line.get("stroke"):
            lines.append(f'(** -> **)[*].style.stroke: "{line_stroke}"')
        line_font_color = line.get("font-color") or line.get("font_color")
        if line_font_color:
            lines.append(f'(** -> **)[*].style.font-color: "{line_font_color}"')

        if bg_fill := background.get("fill"):
            lines.append(f'style.fill: "{bg_fill}"')

        if not lines:
            return source

        directives = "\n".join(lines)
        return f"{directives}\n{source}"

    def _inject_structurizr(self, source: str) -> str:
        element_props: list[str] = []
        person_props: list[str] = []
        relationship_props: list[str] = []
        box = self._styles.get("box", {})
        actor = self._styles.get("actor", {})
        text = self._styles.get("text", {})
        line = self._styles.get("line", {})
        background = self._styles.get("background", {})

        if box_fill := box.get("fill"):
            element_props.append(f"            background {box_fill}")
        if box_stroke := box.get("stroke"):
            element_props.append(f"            stroke {box_stroke}")
        text_color = text.get("fill") or text.get("color")
        if text_color:
            element_props.append(f"            color {text_color}")
        if text_size := text.get("font-size"):
            element_props.append(f"            fontSize {text_size}")

        if actor_fill := actor.get("fill"):
            person_props.append(f"            background {actor_fill}")
        if actor_stroke := actor.get("stroke"):
            person_props.append(f"            stroke {actor_stroke}")
        if text_color:
            person_props.append(f"            color {text_color}")

        if line_stroke := line.get("stroke"):
            relationship_props.append(f"            color {line_stroke}")

        if (
            not element_props
            and not person_props
            and not relationship_props
            and not background.get("fill")
        ):
            return source

        styles_lines: list[str] = []
        if element_props:
            props = "\n".join(element_props)
            styles_lines.append(f'        element "Element" {{\n{props}\n        }}')
        if person_props:
            props = "\n".join(person_props)
            styles_lines.append(f'        element "Person" {{\n{props}\n        }}')
        if relationship_props:
            props = "\n".join(relationship_props)
            styles_lines.append(
                f'        relationship "Relationship" {{\n{props}\n        }}'
            )

        if not styles_lines:
            return source

        styles_block = "\n".join(styles_lines)
        return self._inject_structurizr_styles(source, styles_block)

    @staticmethod
    def _inject_structurizr_styles(source: str, styles_content: str) -> str:
        """Inject styles into a Structurizr DSL source.

        Looks for an existing `styles {` block inside `views {` and injects
        into it. If no styles block exists, creates one inside views.
        """
        # Look for existing "styles {" block
        styles_match = re.search(r"^(\s*styles\s*\{)", source, re.MULTILINE)
        if styles_match:
            insert_pos = styles_match.end()
            return source[:insert_pos] + "\n" + styles_content + source[insert_pos:]

        # No styles block — find "views {" and inject before its closing brace
        views_match = re.search(r"^(\s*views\s*\{)", source, re.MULTILINE)
        if views_match:
            # Find the closing brace of the views block by counting braces
            depth = 0
            pos = views_match.start()
            for i in range(pos, len(source)):
                if source[i] == "{":
                    depth += 1
                elif source[i] == "}":
                    depth -= 1
                    if depth == 0:
                        # Insert styles block before this closing brace
                        styles_block = f"    styles {{\n{styles_content}\n    }}\n"
                        return source[:i] + styles_block + source[i:]

        return source

    @staticmethod
    def _inject_after_opening_brace(source: str, directives: str) -> str:
        """Insert directives after the first opening brace in the source."""
        brace_pos = source.find("{")
        if brace_pos == -1:
            return source
        insert_pos = brace_pos + 1
        return source[:insert_pos] + "\n" + directives + source[insert_pos:]
