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
class ErrorResult:
    err_msg: str
    error: None | Exception = None
    response_text: None | str = None


@dataclass
class MkDocsEventContext:
    page: MkDocsPage
    config: MkDocsConfig
    files: MkDocsFiles


@dataclass
class KrokiImageContext:
    endpoint: str
    options: dict
    data: Result[str, ErrorResult]
