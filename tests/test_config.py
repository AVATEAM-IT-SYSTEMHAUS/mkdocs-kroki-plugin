import pytest

from tests.utils import MkDocsHelper


@pytest.mark.usefixtures("kroki_dummy")
def test_custom_request_timeout(monkeypatch) -> None:
    """Test that custom timeout configuration is used in HTTP requests."""
    # Track the timeout value passed to httpx
    captured_timeout = None

    async def mock_post_with_timeout_capture(*args, **kwargs):
        nonlocal captured_timeout
        captured_timeout = kwargs.get("timeout")
        # Call the original mock from kroki_dummy fixture
        from tests.conftest import MockResponse

        return MockResponse(status_code=200, content=b"<svg>dummy data</svg>")

    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        # Add custom timeout to configuration
        plugin_config = mkdocs_helper._get_plugin_config_entry()
        plugin_config["RequestTimeout"] = 25
        mkdocs_helper.set_http_method("POST")

        # Patch the post method to capture timeout
        monkeypatch.setattr("httpx.AsyncClient.post", mock_post_with_timeout_capture)

        # Act
        result = mkdocs_helper.invoke_build()

        # Assert
        assert result.exit_code == 0
        assert captured_timeout == 25.0, (
            f"Expected timeout to be 25.0 seconds, but got {captured_timeout}"
        )


@pytest.mark.usefixtures("kroki_dummy")
def test_default_request_timeout(monkeypatch) -> None:
    """Test that default timeout of 10.0 seconds is used when not configured."""
    # Track the timeout value passed to httpx
    captured_timeout = None

    async def mock_post_with_timeout_capture(*args, **kwargs):
        nonlocal captured_timeout
        captured_timeout = kwargs.get("timeout")
        from tests.conftest import MockResponse

        return MockResponse(status_code=200, content=b"<svg>dummy data</svg>")

    # Arrange
    with MkDocsHelper("happy_path") as mkdocs_helper:
        # Don't set RequestTimeout - should use default
        mkdocs_helper.set_http_method("POST")

        # Patch the post method to capture timeout
        monkeypatch.setattr("httpx.AsyncClient.post", mock_post_with_timeout_capture)

        # Act
        result = mkdocs_helper.invoke_build()

        # Assert
        assert result.exit_code == 0
        assert captured_timeout == 10.0, (
            f"Expected default timeout to be 10.0 seconds, but got {captured_timeout}"
        )
