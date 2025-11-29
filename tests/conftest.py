import tempfile
from dataclasses import dataclass

import httpx
import pytest

from kroki.diagram_types import KrokiDiagramTypes


@pytest.fixture(autouse=True)
def isolated_cache(monkeypatch):
    """Use a temporary cache directory for each test to avoid cross-test contamination."""
    tmpdir = tempfile.mkdtemp()
    # Point XDG_CACHE_HOME to the temporary directory
    monkeypatch.setenv("XDG_CACHE_HOME", tmpdir)


@pytest.fixture(autouse=True)
def no_actual_requests_please(monkeypatch):
    """Safeguard for missing requests mocks."""
    monkeypatch.delattr("httpx.AsyncClient.request")


@pytest.fixture
def mock_kroki_diagram_types() -> KrokiDiagramTypes:
    return KrokiDiagramTypes(
        "",
        ["svg"],
        {},
        blockdiag_enabled=True,
        bpmn_enabled=True,
        excalidraw_enabled=True,
        mermaid_enabled=True,
        diagramsnet_enabled=True,
    )


@dataclass
class MockResponse:
    status_code: int
    content: None | bytes = None
    text: None | str = None

    @property
    def reason_phrase(self) -> str:
        return httpx.codes.get_reason_phrase(self.status_code)


@pytest.fixture
def kroki_timeout(monkeypatch) -> None:
    """Let request post calls always raise a ConnectionTimeout."""

    async def mock_post(*_args, **_kwargs):
        raise httpx.ConnectTimeout("Connection timeout")

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)


@pytest.fixture
def kroki_bad_request(monkeypatch) -> None:
    """Let request post calls always return a mocked response with status code 400"""

    async def mock_post(*_args, **_kwargs):
        return MockResponse(status_code=400, text="Error 400: Syntax Error? (line: 10)")

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)


@pytest.fixture
def kroki_is_a_teapot(monkeypatch) -> None:
    """Let request post calls always return a mocked response with status code 418"""

    async def mock_post(*_args, **_kwargs):
        return MockResponse(status_code=418)

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)


@pytest.fixture
def kroki_dummy(monkeypatch) -> None:
    """Let request post calls always return a mocked response with status code 200 and dummy content data"""

    async def mock_post(*_args, **_kwargs):
        return MockResponse(status_code=200, content=b"<svg>dummy data</svg>")

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
