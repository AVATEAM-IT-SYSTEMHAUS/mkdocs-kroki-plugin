import os
import pathlib
import shutil
import tempfile
from contextlib import AbstractContextManager
from pathlib import Path
from string import Template
from typing import Final, Literal

import yaml
from click.testing import CliRunner, Result
from mkdocs.__main__ import build_command

from kroki.logging import log
from tests.compat import chdir


def get_expected_log_line(log_msg: str) -> str:
    return f"{log.prefix}: {log_msg}"


class NoPluginEntryError(ValueError):
    def __init__(self) -> None:
        super().__init__("No kroki plugin entry found")


class MkDocsHelper(AbstractContextManager):
    class Context:
        def __init__(self, test_dir: Path) -> None:
            self.test_dir: Final[Path] = test_dir
            self.config_file_path: Final[Path] = test_dir / "mkdocs.yml"
            with open(self.test_dir / "mkdocs.yml") as file:
                self.config_file = yaml.safe_load(file)

        def _dump_config(self) -> None:
            with open(self.config_file_path, mode="w") as file:
                yaml.safe_dump(self.config_file, file)

        def _get_plugin_config_entry(self) -> dict:
            for plugin_entry in self.config_file["plugins"]:
                if "kroki" in plugin_entry:
                    return plugin_entry["kroki"]
            raise NoPluginEntryError

        def enable_fail_fast(self) -> None:
            self._get_plugin_config_entry()["fail_fast"] = True

        def set_http_method(self, method: Literal["GET", "POST"]) -> None:
            self._get_plugin_config_entry()["http_method"] = method

        def set_fence_prefix(self, fence_prefix: str) -> None:
            self._get_plugin_config_entry()["fence_prefix"] = fence_prefix

        def set_tag_format(self, tag_format: Literal["img", "object", "svg"]) -> None:
            self._get_plugin_config_entry()["tag_format"] = tag_format

        def set_diagram_background_color_light(self, color: str) -> None:
            self._get_plugin_config_entry()["diagram_background_color_light"] = color

        def set_diagram_background_color_dark(self, color: str) -> None:
            self._get_plugin_config_entry()["diagram_background_color_dark"] = color

        def invoke_build(self) -> Result:
            self._dump_config()
            runner = CliRunner()
            with chdir(self.test_dir):
                return runner.invoke(build_command)

    def __init__(self, test_case: str) -> None:
        self.test_case = test_case
        self.test_dir = Path(tempfile.mkdtemp())

    def _copy_test_case(self) -> None:
        # equals to `../data`, using current source file as a pin
        data_dir = pathlib.Path(os.path.realpath(__file__)).parent / "data"
        shutil.copytree(data_dir / self.test_case, self.test_dir, dirs_exist_ok=True)

    def __enter__(self) -> Context:
        self._copy_test_case()
        return MkDocsHelper.Context(self.test_dir)

    def __exit__(self, *_args) -> None:
        shutil.rmtree(self.test_dir)


class MkDocsTemplateHelper(MkDocsHelper):
    def _substitute_code_block(self):
        with open(self.test_dir / "docs/index.md") as in_file:
            file_content = Template(in_file.read())
            with open(self.test_dir / "docs/index.md", "w") as out_file:
                out_file.write(file_content.substitute(code_block=self.code_block))

    def __init__(self, code_block: str) -> None:
        super().__init__("template")
        self.code_block = code_block

    def __enter__(self) -> MkDocsHelper.Context:
        context = super().__enter__()
        self._substitute_code_block()
        return context
