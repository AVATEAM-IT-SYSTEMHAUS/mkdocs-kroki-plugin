import logging
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


class MkDocsConfigFile(AbstractContextManager):
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.config_file = None

    def __enter__(self) -> "MkDocsConfigFile":
        with open(self.data_dir / "mkdocs.yml") as file:
            self.config_file = yaml.safe_load(file)
        return self

    def __exit__(self, *_args) -> None:
        with open(self.data_dir / "mkdocs.yml", mode="w") as file:
            yaml.safe_dump(self.config_file, file)

    def _get_plugin_config_entry(self) -> dict:
        for plugin_entry in self.config_file["plugins"]:
            if "kroki" in plugin_entry:
                return plugin_entry["kroki"]
        raise NoPluginEntryError

    def enable_fail_fast(self) -> None:
        self._get_plugin_config_entry()["FailFast"] = True

    def set_http_method(self, method: Literal["GET", "POST"]) -> None:
        self._get_plugin_config_entry()["HttpMethod"] = method


class MkDocsHelper:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def invoke_build(self) -> Result:
        runner = CliRunner()
        with chdir(self.data_dir):
            return runner.invoke(build_command)
