import pytest

from tests.utils import MkDocsHelper


@pytest.mark.usefixtures("kroki_timeout")
def test_request_timeout() -> None:
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.enable_fail_fast()

        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 1
        assert "Request error" in result.output
        assert "Aborted with a BuildError!" in result.output


@pytest.mark.usefixtures("kroki_bad_request")
def test_request_bad_request() -> None:
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.enable_fail_fast()

        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 1
        assert "Diagram error!" in result.output
        assert "Aborted with a BuildError!" in result.output


@pytest.mark.usefixtures("kroki_is_a_teapot")
def test_request_other_error() -> None:
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.enable_fail_fast()

        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 1
        assert "Could not retrieve image data" in result.output
        assert "Aborted with a BuildError!" in result.output


@pytest.mark.usefixtures("kroki_dummy")
def test_missing_file_from() -> None:
    with MkDocsHelper("missing_from_file") as mkdocs_helper:
        mkdocs_helper.enable_fail_fast()

        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 1
        assert "kroki: Can't read file:" in result.output
        assert "Aborted with a BuildError!" in result.output
