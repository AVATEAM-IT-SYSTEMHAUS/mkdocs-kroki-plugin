import pytest

from tests.utils import MkDocsHelper


class TestErrors:
    @pytest.mark.usefixtures("kroki_timeout")
    def test_request_timeout(self) -> None:
        with MkDocsHelper("happy_path") as mkdocs_helper:
            mkdocs_helper.set_http_method("POST")

            result = mkdocs_helper.invoke_build()

            assert result.exit_code == 0
            assert "kroki: Request error" in result.output
            with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
                assert '<p>!!! error "Request error' in index_html_file.read()

    @pytest.mark.usefixtures("kroki_bad_request")
    def test_request_bad_request(self) -> None:
        with MkDocsHelper("happy_path") as mkdocs_helper:
            mkdocs_helper.set_http_method("POST")

            result = mkdocs_helper.invoke_build()

            assert result.exit_code == 0
            assert "kroki: Diagram error!" in result.output
            with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
                assert '<p>!!! error "Diagram error!"</p>' in index_html_file.read()

    @pytest.mark.usefixtures("kroki_is_a_teapot")
    def test_request_other_error(self) -> None:
        with MkDocsHelper("happy_path") as mkdocs_helper:
            mkdocs_helper.set_http_method("POST")

            result = mkdocs_helper.invoke_build()

            assert result.exit_code == 0
            assert "Could not retrieve image data" in result.output
            with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
                assert '<p>!!! error "Could not retrieve image data' in index_html_file.read()

    @pytest.mark.usefixtures("kroki_dummy")
    def test_missing_file_from(self) -> None:
        with MkDocsHelper("missing_from_file") as mkdocs_helper:
            mkdocs_helper.set_http_method("POST")
            result = mkdocs_helper.invoke_build()

            assert result.exit_code == 0
            assert "kroki: Can't read file:" in result.output
            with open(mkdocs_helper.test_dir / "site/index.html") as index_html_file:
                assert "<p>!!! error \"Can't read file: " in index_html_file.read()
