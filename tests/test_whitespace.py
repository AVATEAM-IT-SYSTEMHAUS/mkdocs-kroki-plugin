from pathlib import Path

import pytest

from tests.utils import MkDocsHelper


def _set_whitespace_after_fenced_block(test_dir: Path):
    with open(test_dir / "docs/index.md") as in_file:
        file_content = in_file.read()
        with open(test_dir / "docs/index.md", "w") as out_file:
            out_file.write(file_content.replace("```c4plantuml", "``` c4plantuml"))


@pytest.mark.usefixtures("kroki_dummy")
def test_whitespace_in_fence_prefix() -> None:
    with MkDocsHelper("happy_path") as mkdocs_helper:
        _set_whitespace_after_fenced_block(mkdocs_helper.test_dir)
        mkdocs_helper.set_http_method("POST")
        mkdocs_helper.set_fence_prefix(" ")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0
        image_files = list((mkdocs_helper.test_dir / "site").glob("*.svg"))
        assert len(image_files) == 1
