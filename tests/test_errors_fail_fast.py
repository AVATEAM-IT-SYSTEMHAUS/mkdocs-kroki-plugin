from pathlib import Path

import pytest

from tests.utils import MkDocsConfigFile, MkDocsHelper


@pytest.mark.usefixtures("kroki_timeout")
def test_request_timeout(datadir_happy_path: Path) -> None:
    with MkDocsConfigFile(datadir_happy_path) as config:
        config.enable_fail_fast()
        config.set_http_method("POST")

    mkdocs_helper = MkDocsHelper(datadir_happy_path)
    result = mkdocs_helper.invoke_build()

    assert result.exit_code == 1
    assert "Request error" in result.output
    assert "Aborted with a BuildError!" in result.output


@pytest.mark.usefixtures("kroki_bad_request")
def test_request_bad_request(datadir_happy_path: Path) -> None:
    with MkDocsConfigFile(datadir_happy_path) as config:
        config.enable_fail_fast()
        config.set_http_method("POST")

    mkdocs_helper = MkDocsHelper(datadir_happy_path)
    result = mkdocs_helper.invoke_build()

    assert result.exit_code == 1
    assert "Diagram error!" in result.output
    assert "Aborted with a BuildError!" in result.output


@pytest.mark.usefixtures("kroki_is_a_teapot")
def test_request_other_error(datadir_happy_path: Path) -> None:
    with MkDocsConfigFile(datadir_happy_path) as config:
        config.enable_fail_fast()
        config.set_http_method("POST")

    mkdocs_helper = MkDocsHelper(datadir_happy_path)
    result = mkdocs_helper.invoke_build()

    assert result.exit_code == 1
    assert "Could not retrieve image data" in result.output
    assert "Aborted with a BuildError!" in result.output


@pytest.mark.usefixtures("kroki_dummy")
def test_missing_file_from(datadir_missing_from_file: Path) -> None:
    with MkDocsConfigFile(datadir_missing_from_file) as config:
        config.enable_fail_fast()

    mkdocs_helper = MkDocsHelper(datadir_missing_from_file)
    result = mkdocs_helper.invoke_build()

    assert result.exit_code == 1
    assert "kroki: Can't read file:" in result.output
    assert "Aborted with a BuildError!" in result.output
