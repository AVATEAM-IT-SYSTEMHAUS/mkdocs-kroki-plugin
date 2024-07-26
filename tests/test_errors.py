import bs4
import pytest

from tests.utils import MkDocsHelper, get_expected_log_line


def _assert_error_block(err_msg: str, index_html: str):
    index_soup = bs4.BeautifulSoup(index_html)
    details_tag = index_soup.find("details")
    assert isinstance(details_tag, bs4.Tag), "Error message container not in resulting HTML"
    summary_tag = details_tag.summary
    assert isinstance(summary_tag, bs4.Tag), "Error message container has no summary element"
    assert err_msg in summary_tag.text


@pytest.mark.usefixtures("kroki_timeout")
def test_request_timeout() -> None:
    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 0
        assert get_expected_log_line("Request error") in result.output
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            _assert_error_block("Request error", index_html_file.read())


@pytest.mark.usefixtures("kroki_bad_request")
def test_request_bad_request() -> None:
    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 0
        assert get_expected_log_line("Diagram error!") in result.output
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            _assert_error_block("Diagram error!", index_html_file.read())


@pytest.mark.usefixtures("kroki_is_a_teapot")
def test_request_other_error() -> None:
    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 0
        assert get_expected_log_line("Could not retrieve image data") in result.output
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            _assert_error_block("Could not retrieve image data", index_html_file.read())


@pytest.mark.usefixtures("kroki_dummy")
def test_missing_from_file() -> None:
    # Arrange
    with MkDocsHelper("missing_from_file") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        # Act
        result = mkdocs_helper.invoke_build()
        # Assert
        assert result.exit_code == 0
        assert get_expected_log_line("Can't read file:") in result.output
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            _assert_error_block("Can't read file: ", index_html_file.read())
