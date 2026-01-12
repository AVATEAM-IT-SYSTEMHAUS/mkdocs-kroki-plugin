import bs4
import pytest

from tests.utils import MkDocsTemplateHelper


@pytest.mark.usefixtures("kroki_dummy")
def test_global_background_light_only() -> None:
    """Test that global diagram_background_color_light sets background style."""
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_diagram_background_color_light("white")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        style = img_tag.get("style", "")
        assert "background: white" in style
        assert "light-dark" not in style


@pytest.mark.usefixtures("kroki_dummy")
def test_global_background_dark_only() -> None:
    """Test that global diagram_background_color_dark sets background style."""
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_diagram_background_color_dark("#1a1a1a")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        style = img_tag.get("style", "")
        assert "background: #1a1a1a" in style
        assert "light-dark" not in style


@pytest.mark.usefixtures("kroki_dummy")
def test_global_background_light_and_dark() -> None:
    """Test that both global colors use light-dark() CSS function."""
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_diagram_background_color_light("white")
        mkdocs_helper.set_diagram_background_color_dark("#333")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        style = img_tag.get("style", "")
        assert "background: light-dark(white, #333)" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_per_diagram_bg_light_override() -> None:
    """Test that per-diagram bg-light overrides global setting."""
    code_block = """```plantuml {bg-light=#eee}
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_diagram_background_color_light("white")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        style = img_tag.get("style", "")
        assert "background: #eee" in style
        assert "white" not in style


@pytest.mark.usefixtures("kroki_dummy")
def test_per_diagram_bg_dark_override() -> None:
    """Test that per-diagram bg-dark overrides global setting."""
    code_block = """```plantuml {bg-dark=#222}
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_diagram_background_color_dark("#333")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        style = img_tag.get("style", "")
        assert "background: #222" in style
        assert "#333" not in style


@pytest.mark.usefixtures("kroki_dummy")
def test_per_diagram_both_bg_override() -> None:
    """Test that per-diagram options override both global settings."""
    code_block = """```plantuml {bg-light=#fff bg-dark=#000}
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_diagram_background_color_light("white")
        mkdocs_helper.set_diagram_background_color_dark("#333")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        style = img_tag.get("style", "")
        assert "background: light-dark(#fff, #000)" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_per_diagram_bg_without_global() -> None:
    """Test that per-diagram bg options work without global settings."""
    code_block = """```plantuml {bg-light=yellow bg-dark=navy}
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
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        style = img_tag.get("style", "")
        assert "background: light-dark(yellow, navy)" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_background_on_object_tag() -> None:
    """Test that background color works with object tag format."""
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("object")
        mkdocs_helper.set_diagram_background_color_light("white")
        mkdocs_helper.set_diagram_background_color_dark("#333")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        object_tag = soup.find("object", attrs={"id": "Kroki"})
        assert object_tag is not None
        style = object_tag.get("style", "")
        assert "background: light-dark(white, #333)" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_background_on_svg_tag() -> None:
    """Test that background color works with inline SVG."""
    code_block = """```plantuml
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("svg")
        mkdocs_helper.set_diagram_background_color_light("white")
        mkdocs_helper.set_diagram_background_color_dark("#333")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        svg_tag = soup.find("svg", attrs={"id": "Kroki"})
        assert svg_tag is not None
        style = svg_tag.get("style", "")
        assert "background: light-dark(white, #333)" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_background_combined_with_display_options() -> None:
    """Test that background color works together with display options."""
    code_block = """```plantuml {display-width=500px display-align=center}
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_diagram_background_color_light("white")
        mkdocs_helper.set_diagram_background_color_dark("#333")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        style = img_tag.get("style", "")
        assert "width: 500px" in style
        assert "display: block" in style
        assert "margin-left: auto" in style
        assert "background: light-dark(white, #333)" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_no_background_when_not_set() -> None:
    """Test that no background is added when options are not set."""
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
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        assert img_tag.get("style") is None


@pytest.mark.usefixtures("kroki_dummy")
def test_per_diagram_partial_override() -> None:
    """Test that per-diagram can override only one color while using global for the other."""
    code_block = """```plantuml {bg-light=#eee}
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("img")
        mkdocs_helper.set_diagram_background_color_light("white")
        mkdocs_helper.set_diagram_background_color_dark("#333")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        img_tag = soup.find("img", attrs={"alt": "Kroki"})
        assert img_tag is not None
        style = img_tag.get("style", "")
        # bg-light is overridden to #eee, bg-dark uses global #333
        assert "background: light-dark(#eee, #333)" in style
