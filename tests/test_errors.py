from pathlib import Path

import pytest

from tests.utils import MkDocsConfigFile, MkDocsHelper


@pytest.mark.usefixtures("kroki_timeout")
def test_request_timeout(datadir_happy_path: Path) -> None:
    with MkDocsConfigFile(datadir_happy_path) as config:
        config.set_http_method("POST")

    mkdocs_helper = MkDocsHelper(datadir_happy_path)
    result = mkdocs_helper.invoke_build()

    assert result.exit_code == 0
    assert "kroki: Request error" in result.output
    with open(datadir_happy_path / "site/index.html") as index_html_file:
        assert '<p>!!! error "Request error' in index_html_file.read()


@pytest.mark.usefixtures("kroki_bad_request")
def test_request_bad_request(datadir_happy_path: Path) -> None:
    with MkDocsConfigFile(datadir_happy_path) as config:
        config.set_http_method("POST")

    mkdocs_helper = MkDocsHelper(datadir_happy_path)
    result = mkdocs_helper.invoke_build()

    assert result.exit_code == 0
    assert "kroki: Diagram error!" in result.output
    with open(datadir_happy_path / "site/index.html") as index_html_file:
        assert '<p>!!! error "Diagram error!"</p>' in index_html_file.read()


@pytest.mark.usefixtures("kroki_is_a_teapot")
def test_request_other_error(datadir_happy_path: Path) -> None:
    with MkDocsConfigFile(datadir_happy_path) as config:
        config.set_http_method("POST")

    mkdocs_helper = MkDocsHelper(datadir_happy_path)
    result = mkdocs_helper.invoke_build()

    assert result.exit_code == 0
    assert "Could not retrieve image data" in result.output
    with open(datadir_happy_path / "site/index.html") as index_html_file:
        assert '<p>!!! error "Could not retrieve image data' in index_html_file.read()


@pytest.mark.usefixtures("kroki_dummy")
def test_missing_file_from(datadir_missing_from_file: Path) -> None:
    mkdocs_helper = MkDocsHelper(datadir_missing_from_file)
    result = mkdocs_helper.invoke_build()

    assert result.exit_code == 0
    assert "kroki: Can't read file:" in result.output
    with open(datadir_missing_from_file / "site/index.html") as index_html_file:
        assert "<p>!!! error \"Can't read file: " in index_html_file.read()
