import bs4
import pytest

from tests.utils import MkDocsTemplateHelper


@pytest.mark.usefixtures("kroki_dummy")
def test_block_inside_html() -> None:
    # Arrange
    with MkDocsTemplateHelper("""
<details>
    <summary><u>Show Sequence diagram...</u></summary>
```mermaid
graph TD
    a --> b
```
</details>

```mermaid
graph TD
    a --> b
```
""") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 0, f"exit code {result.exit_code}, expected 0"
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html:
            index_soup = bs4.BeautifulSoup(index_html.read())
            assert len(index_soup.find_all("object", attrs={"name": "Kroki"})) == 2, "not all image were included"
