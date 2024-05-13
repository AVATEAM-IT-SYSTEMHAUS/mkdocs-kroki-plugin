import logging
import os
import pathlib
import shutil
import tempfile
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Literal

import yaml
from click.testing import CliRunner, Result
from mkdocs.__main__ import build_command

from tests.compat import chdir

logging.basicConfig(level=logging.INFO)


class NoPluginEntryError(ValueError):
    def __init__(self) -> None:
        super().__init__("No kroki plugin entry found")


class MkDocsHelper(AbstractContextManager):
    def __init__(self, test_case: str) -> None:
        self.config_file = None
        self.test_case = test_case
        self.test_dir = Path(tempfile.mkdtemp())

    def _copy_test_case(self) -> None:
        # equals to `../data`, using current source file as a pin
        data_dir = pathlib.Path(os.path.realpath(__file__)).parent / "data"
        shutil.copytree(data_dir / self.test_case, self.test_dir, dirs_exist_ok=True)

    def _load_config(self) -> None:
        with open(self.test_dir / "mkdocs.yml") as file:
            self.config_file = yaml.safe_load(file)

    def _dump_config(self) -> None:
        with open(self.test_dir / "mkdocs.yml", mode="w") as file:
            yaml.safe_dump(self.config_file, file)

    def __enter__(self) -> "MkDocsHelper":
        self._copy_test_case()
        self._load_config()

        return self

    def __exit__(self, *_args) -> None:
        shutil.rmtree(self.test_dir)

    def _get_plugin_config_entry(self) -> dict:
        for plugin_entry in self.config_file["plugins"]:
            if "kroki" in plugin_entry:
                return plugin_entry["kroki"]
        raise NoPluginEntryError

    def enable_fail_fast(self) -> None:
        self._get_plugin_config_entry()["FailFast"] = True

    def set_http_method(self, method: Literal["GET", "POST"]) -> None:
        self._get_plugin_config_entry()["HttpMethod"] = method

    def invoke_build(self) -> Result:
        self._dump_config()
        runner = CliRunner()
        with chdir(self.test_dir):
            return runner.invoke(build_command)
