from dataclasses import dataclass

import pytest
import requests

from kroki.diagram_types import KrokiDiagramTypes


@pytest.fixture(autouse=True)
def no_actual_requests_please(monkeypatch):
    """Safeguard for missing requests mocks."""
    monkeypatch.delattr("requests.sessions.Session.request")


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
    def reason(self) -> str:
        return requests.codes.get(self.status_code)


@pytest.fixture
def kroki_timeout(monkeypatch) -> None:
    """Let request post calls always raise a ConnectionTimeout."""

    def mock_post(*_args, **_kwargs):
        raise requests.exceptions.ConnectTimeout

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture
def kroki_bad_request(monkeypatch) -> None:
    """Let request post calls always return a mocked response with status code 400"""

    def mock_post(*_args, **_kwargs):
        return MockResponse(status_code=400, text="Error 400: Syntax Error? (line: 10)")

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture
def kroki_is_a_teapot(monkeypatch) -> None:
    """Let request post calls always return a mocked response with status code 418"""

    def mock_post(*_args, **_kwargs):
        return MockResponse(status_code=418)

    monkeypatch.setattr(requests, "post", mock_post)


@pytest.fixture
def kroki_dummy(monkeypatch) -> None:
    """Let request post calls always return a mocked response with status code 200 and dummy content data"""

    def mock_post(*_args, **_kwargs):
        return MockResponse(status_code=200, content=b"<svg>dummy data</svg>")

    monkeypatch.setattr(requests, "post", mock_post)
