import pytest

from tests.utils import MkDocsHelper, get_expected_log_line


@pytest.mark.usefixtures("kroki_timeout")
def test_request_timeout() -> None:
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")

        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        assert get_expected_log_line("Request error") in result.output
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            assert '<p>!!! error "Request error' in index_html_file.read()
            # assert '<summary>Request error' in index_html_file.read()


@pytest.mark.usefixtures("kroki_bad_request")
def test_request_bad_request() -> None:
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")

        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        assert get_expected_log_line("Diagram error!") in result.output
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            assert '<p>!!! error "Diagram error!"' in index_html_file.read()
            # assert '<summary>Diagram error!</summary>' in index_html_file.read()


@pytest.mark.usefixtures("kroki_is_a_teapot")
def test_request_other_error() -> None:
    with MkDocsHelper("happy_path") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")

        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        assert get_expected_log_line("Could not retrieve image data") in result.output
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            assert '<p>!!! error "Could not retrieve image data' in index_html_file.read()
            # assert '<summary>Could not retrieve image data' in index_html_file.read()


@pytest.mark.usefixtures("kroki_dummy")
def test_missing_file_from() -> None:
    with MkDocsHelper("missing_from_file") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        assert get_expected_log_line("Can't read file:") in result.output
        with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
            assert "<p>!!! error \"Can't read file: " in index_html_file.read()
            # assert "<summary>Can't read file: " in index_html_file.read()
