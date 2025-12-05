import bs4
import pytest

from tests.utils import MkDocsTemplateHelper


@pytest.mark.usefixtures("kroki_dummy")
def test_display_width_on_img_tag() -> None:
    """Test that display-width option sets width style on img tag."""
    code_block = """```plantuml {display-width=500px}
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
        assert "width: 500px" in img_tag.get("style", "")


@pytest.mark.usefixtures("kroki_dummy")
def test_display_height_on_img_tag() -> None:
    """Test that display-height option sets height style on img tag."""
    code_block = """```plantuml {display-height=300px}
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
        assert "height: 300px" in img_tag.get("style", "")


@pytest.mark.usefixtures("kroki_dummy")
def test_display_width_and_height_on_img_tag() -> None:
    """Test that both display-width and display-height work together."""
    code_block = """```plantuml {display-width=500px display-height=300px}
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
        assert "width: 500px" in style
        assert "height: 300px" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_display_options_on_object_tag() -> None:
    """Test that display options work with object tag format."""
    code_block = """```plantuml {display-width=600px display-height=400px}
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("object")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        object_tag = soup.find("object", attrs={"id": "Kroki"})
        assert object_tag is not None
        style = object_tag.get("style", "")
        assert "width: 600px" in style
        assert "height: 400px" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_display_options_on_svg_tag() -> None:
    """Test that display options work with inline SVG."""
    code_block = """```plantuml {display-width=700px display-height=500px}
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("svg")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as f:
            soup = bs4.BeautifulSoup(f.read(), features="html.parser")

        svg_tag = soup.find("svg", attrs={"id": "Kroki"})
        assert svg_tag is not None
        style = svg_tag.get("style", "")
        assert "width: 700px" in style
        assert "height: 500px" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_display_options_not_sent_to_kroki_server(mocker) -> None:
    """Test that display-* options are filtered out before sending to Kroki."""
    code_block = """```plantuml {display-width=500px theme=dark}
@startuml
A -> B
@enduml
```"""
    with MkDocsTemplateHelper(code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0


@pytest.mark.usefixtures("kroki_dummy")
def test_no_display_options_no_style() -> None:
    """Test that without display options, no style attribute is added."""
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
def test_display_align_center() -> None:
    """Test that display-align=center sets block display with auto margins."""
    code_block = """```plantuml {display-align=center}
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
        assert "display: block" in style
        assert "margin-left: auto" in style
        assert "margin-right: auto" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_display_align_right() -> None:
    """Test that display-align=right sets block display with left auto margin."""
    code_block = """```plantuml {display-align=right}
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
        assert "display: block" in style
        assert "margin-left: auto" in style
        assert "margin-right: 0" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_display_align_left() -> None:
    """Test that display-align=left sets block display with right auto margin."""
    code_block = """```plantuml {display-align=left}
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
        assert "display: block" in style
        assert "margin-left: 0" in style
        assert "margin-right: auto" in style


@pytest.mark.usefixtures("kroki_dummy")
def test_display_align_with_width() -> None:
    """Test that display-align works together with display-width."""
    code_block = """```plantuml {display-width=400px display-align=center}
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
        assert "width: 400px" in style
        assert "display: block" in style
        assert "margin-left: auto" in style
        assert "margin-right: auto" in style
