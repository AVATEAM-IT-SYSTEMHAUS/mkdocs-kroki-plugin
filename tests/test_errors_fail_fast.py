import pytest

from tests.utils import MkDocsHelper, get_expected_log_line


@pytest.mark.usefixtures("kroki_timeout")
def test_request_timeout() -> None:
    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.enable_fail_fast()
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 1
        assert get_expected_log_line("Request error") in result.output
        assert "Aborted with a BuildError!" in result.output


@pytest.mark.usefixtures("kroki_bad_request")
def test_request_bad_request() -> None:
    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.enable_fail_fast()
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 1
        assert get_expected_log_line("Diagram error!") in result.output
        assert "Aborted with a BuildError!" in result.output


@pytest.mark.usefixtures("kroki_is_a_teapot")
def test_request_other_error() -> None:
    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.enable_fail_fast()
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 1
        assert get_expected_log_line("Could not retrieve image data") in result.output
        assert "Aborted with a BuildError!" in result.output


@pytest.mark.usefixtures("kroki_dummy")
def test_missing_file_from() -> None:
    # Arrange
    with MkDocsHelper("missing_from_file") as mkdocs_helper:
        mkdocs_helper.enable_fail_fast()
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 1
        assert get_expected_log_line("Can't read file:") in result.output
        assert "Aborted with a BuildError!" in result.output
