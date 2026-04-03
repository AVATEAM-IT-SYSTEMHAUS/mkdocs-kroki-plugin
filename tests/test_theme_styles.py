import textwrap
from unittest.mock import MagicMock

import bs4
import pytest

from kroki.parsing import MarkdownParser
from kroki.styles import StyleInjector
from tests.utils import MkDocsTemplateHelper

_LIGHT_STYLES = {"box": {"fill": "#e8f4fd", "stroke": "#0066cc"}}
_DARK_STYLES = {"box": {"fill": "#1a2a3a", "stroke": "#4da6ff"}}


# --- Unit tests for MarkdownParser dual injection ---


def test_dual_style_injectors_populate_data_dark(
    mock_kroki_diagram_types, kroki_dummy
) -> None:
    injector_light = StyleInjector(_LIGHT_STYLES)
    injector_dark = StyleInjector(_DARK_STYLES)
    parser = MarkdownParser(
        "/tmp",
        mock_kroki_diagram_types,
        style_injector_light=injector_light,
        style_injector_dark=injector_dark,
    )
    md = textwrap.dedent("""\
        ```plantuml
        @startuml
        Alice -> Bob
        @enduml
        ```
    """)
    captured = []

    async def capture_callback(kroki_context, mkdocs_context):
        captured.append(kroki_context)
        return "<img />"

    parser.replace_kroki_blocks(md, capture_callback, MagicMock())
    assert len(captured) == 1
    ctx = captured[0]
    assert ctx.data_dark is not None
    assert "skinparam RectangleBackgroundColor #e8f4fd" in ctx.data.unwrap()
    assert "skinparam RectangleBackgroundColor #1a2a3a" in ctx.data_dark.unwrap()


def test_single_style_injector_leaves_data_dark_none(
    mock_kroki_diagram_types, kroki_dummy
) -> None:
    parser = MarkdownParser(
        "/tmp",
        mock_kroki_diagram_types,
        style_injector=StyleInjector(_LIGHT_STYLES),
    )
    md = textwrap.dedent("""\
        ```plantuml
        @startuml
        Alice -> Bob
        @enduml
        ```
    """)
    captured = []

    async def capture_callback(kroki_context, mkdocs_context):
        captured.append(kroki_context)
        return "<img />"

    parser.replace_kroki_blocks(md, capture_callback, MagicMock())
    assert captured[0].data_dark is None


def test_no_style_inject_skips_both_injectors(
    mock_kroki_diagram_types, kroki_dummy
) -> None:
    parser = MarkdownParser(
        "/tmp",
        mock_kroki_diagram_types,
        style_injector_light=StyleInjector(_LIGHT_STYLES),
        style_injector_dark=StyleInjector(_DARK_STYLES),
    )
    md = textwrap.dedent("""\
        ```plantuml no-style-inject=true
        @startuml
        Alice -> Bob
        @enduml
        ```
    """)
    captured = []

    async def capture_callback(kroki_context, mkdocs_context):
        captured.append(kroki_context)
        return "<img />"

    parser.replace_kroki_blocks(md, capture_callback, MagicMock())
    ctx = captured[0]
    assert ctx.data_dark is None
    assert "skinparam" not in ctx.data.unwrap()


def test_only_light_injector_set_leaves_data_dark_none(
    mock_kroki_diagram_types, kroki_dummy
) -> None:
    parser = MarkdownParser(
        "/tmp",
        mock_kroki_diagram_types,
        style_injector_light=StyleInjector(_LIGHT_STYLES),
    )
    md = textwrap.dedent("""\
        ```plantuml
        @startuml
        Alice -> Bob
        @enduml
        ```
    """)
    captured = []

    async def capture_callback(kroki_context, mkdocs_context):
        captured.append(kroki_context)
        return "<img />"

    parser.replace_kroki_blocks(md, capture_callback, MagicMock())
    ctx = captured[0]
    assert ctx.data_dark is None
    assert "skinparam RectangleBackgroundColor #e8f4fd" in ctx.data.unwrap()


# --- Integration tests ---


@pytest.mark.usefixtures("kroki_dummy")
def test_dual_styles_renders_two_img_tags() -> None:
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_styles_light(_LIGHT_STYLES)
        mkdocs_helper.set_styles_dark(_DARK_STYLES)
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

    imgs = soup.find_all("img", attrs={"alt": "Kroki"})
    assert len(imgs) == 2

    srcs = [img["src"] for img in imgs]
    assert any("#only-light" in src for src in srcs)
    assert any("#only-dark" in src for src in srcs)


@pytest.mark.usefixtures("kroki_dummy")
def test_dual_styles_each_img_has_correct_hash_fragment() -> None:
    """Each img must carry exactly one of the two theme hash fragments."""
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_styles_light(_LIGHT_STYLES)
        mkdocs_helper.set_styles_dark(_DARK_STYLES)
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

    imgs = soup.find_all("img", attrs={"alt": "Kroki"})
    assert len(imgs) == 2
    light_imgs = [img for img in imgs if img["src"].endswith("#only-light")]
    dark_imgs = [img for img in imgs if img["src"].endswith("#only-dark")]
    assert len(light_imgs) == 1
    assert len(dark_imgs) == 1


@pytest.mark.usefixtures("kroki_dummy")
def test_single_styles_still_renders_single_img() -> None:
    """Existing single-styles behavior is unchanged."""
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_styles_light(_LIGHT_STYLES)
        # Only light set, no dark → single image
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

    imgs = soup.find_all("img", attrs={"alt": "Kroki"})
    assert len(imgs) == 1
    assert "#only-light" not in imgs[0].get("src", "")
    assert "#only-dark" not in imgs[0].get("src", "")


@pytest.mark.usefixtures("kroki_dummy")
def test_dual_styles_with_background_colors() -> None:
    """Background color style attribute is applied to both img tags."""
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_styles_light(_LIGHT_STYLES)
        mkdocs_helper.set_styles_dark(_DARK_STYLES)
        mkdocs_helper.set_diagram_background_color_light("white")
        mkdocs_helper.set_diagram_background_color_dark("#1e1e1e")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

    imgs = soup.find_all("img", attrs={"alt": "Kroki"})
    assert len(imgs) == 2
    for img in imgs:
        assert "light-dark(white, #1e1e1e)" in img.get("style", "")


@pytest.mark.usefixtures("kroki_dummy")
def test_no_dual_styles_when_not_configured() -> None:
    """Without styles_light/styles_dark, no theme hash fragments are added."""
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            content = f.read()

    assert "#only-light" not in content
    assert "#only-dark" not in content
