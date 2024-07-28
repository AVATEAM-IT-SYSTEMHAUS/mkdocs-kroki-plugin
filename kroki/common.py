from dataclasses import dataclass

from mkdocs.config.defaults import MkDocsConfig as _MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page
from result import Result

MkDocsPage = Page
MkDocsConfig = _MkDocsConfig
MkDocsFiles = Files
MkDocsFile = File


@dataclass
class ImageSrc:
    """Information for the renderer."""

    url: str
    file_ext: str
    file_content: None | bytes = None


@dataclass
class ErrorResult:
    err_msg: str
    error: None | Exception = None
    response_text: None | str = None


@dataclass
class MkDocsEventContext:
    """Data supplied by MkDocs on the currently handled page."""

    page: MkDocsPage
    config: MkDocsConfig
    files: MkDocsFiles


@dataclass
class KrokiImageContext:
    """Code block contents that are to be used for the diagram generation."""

    kroki_type: str
    options: dict
    data: Result[str, ErrorResult]
