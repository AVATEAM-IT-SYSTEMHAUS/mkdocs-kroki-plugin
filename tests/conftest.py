import os
import pathlib
import shutil
from dataclasses import dataclass
from pathlib import Path

import pytest
import requests


@pytest.fixture(autouse=True)
def no_actual_requests_please(monkeypatch):
    """Safeguard for missing requests mocks."""
    monkeypatch.delattr("requests.sessions.Session.request")


@dataclass
class MockResponse:
    status_code: int
    content: None | bytes = None


def copy_test_case(tmp_path: Path, test_case: str) -> Path:
    data_dir = pathlib.Path(os.path.realpath(__file__)).parent / "data"
    shutil.copytree(data_dir / test_case, tmp_path, dirs_exist_ok=True)
    return tmp_path


@pytest.fixture
def datadir_happy_path(tmp_path: Path) -> Path:
    return copy_test_case(tmp_path, "happy_path")


@pytest.fixture
def datadir_missing_from_file(tmp_path: Path) -> Path:
    return copy_test_case(tmp_path, "missing_from_file")


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
        return MockResponse(status_code=400)

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
        return MockResponse(status_code=200, content=b"dummy data")

    monkeypatch.setattr(requests, "post", mock_post)
