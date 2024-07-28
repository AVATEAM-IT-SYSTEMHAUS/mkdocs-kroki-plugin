import bs4
import pytest

from tests.utils import MkDocsHelper


@pytest.mark.usefixtures("kroki_dummy")
def test_happy_path() -> None:
    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            index_html = index_html_file.read()

        index_soup = bs4.BeautifulSoup(index_html)
        img_tags = index_soup.find_all("img", attrs={"alt": "Kroki"})

        assert len(img_tags) == 2


@pytest.mark.usefixtures("kroki_dummy")
def test_happy_path_object() -> None:
    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("object")
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            index_html = index_html_file.read()

        index_soup = bs4.BeautifulSoup(index_html)
        img_tags = index_soup.find_all("object", attrs={"id": "Kroki"})

        assert len(img_tags) == 2


@pytest.mark.usefixtures("kroki_dummy")
def test_happy_path_svg() -> None:
    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_tag_format("svg")
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 0
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            index_html = index_html_file.read()

        index_soup = bs4.BeautifulSoup(index_html)
        img_tags = index_soup.find_all("svg", attrs={"id": "Kroki"})

        assert len(img_tags) == 2
