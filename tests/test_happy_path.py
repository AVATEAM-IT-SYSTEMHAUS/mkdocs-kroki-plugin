import bs4
import pytest

from tests.utils import MkDocsHelper


@pytest.mark.usefixtures("kroki_dummy")
def test_missing_from_file() -> None:
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
        img_tags = index_soup.find_all(attrs={"name":"Kroki"})

        assert len(img_tags) == 2
