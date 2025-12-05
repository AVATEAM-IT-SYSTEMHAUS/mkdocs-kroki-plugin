import asyncio
import re
import textwrap
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Final

from result import Err, Ok, Result

from kroki.common import (
    PLUGIN_OPTIONS,
    ErrorResult,
    KrokiImageContext,
    MkDocsEventContext,
)
from kroki.diagram_types import KrokiDiagramTypes
from kroki.logging import log

_FENCE_RE = re.compile(
    r"(?P<fence>^(?P<indent>[ ]*)(?:````*|~~~~*))[ ]*"
    r"(\.?(?P<lang>[\w#.+-]*)[ ]*)?"
    r"(?P<opts>\{[^}]*\}|(?:[ ]?[a-zA-Z0-9\-_]+=[a-zA-Z0-9\-_]+)*)\n"
    r"(?P<code>.*?)(?<=\n)"
    r"(?P=fence)[ ]*$",
    flags=re.IGNORECASE + re.DOTALL + re.MULTILINE,
)
_FROM_FILE_PREFIX: Final[str] = "@from_file:"


class MarkdownParser:
    def __init__(self, docs_dir: str, diagram_types: KrokiDiagramTypes) -> None:
        self.diagram_types = diagram_types
        self.docs_dir = docs_dir

    def _get_block_content(self, block_data: str) -> Result[str, ErrorResult]:
        if not block_data.startswith(_FROM_FILE_PREFIX):
            return Ok(block_data)

        file_name = block_data.removeprefix(_FROM_FILE_PREFIX).strip()
        file_path = Path(self.docs_dir) / file_name
        log.debug('Reading kroki block from file: "%s"', file_path.absolute())
        try:
            with open(file_path) as data_file:
                return Ok(data_file.read())
        except OSError as error:
            return Err(
                ErrorResult(
                    err_msg=f'Can\'t read file: "{file_path.absolute()}" from code block "{block_data}"',
                    error=error,
                )
            )

    def replace_kroki_blocks(
        self,
        markdown: str,
        block_callback: Callable[
            [KrokiImageContext, MkDocsEventContext], Awaitable[str]
        ],
        context: MkDocsEventContext,
    ) -> str:
        # Collect all matches and their contexts
        matches = list(_FENCE_RE.finditer(markdown))
        if not matches:
            return markdown

        # Process matches to build kroki contexts
        tasks: list[Awaitable[str]] = []
        match_data: list[tuple[re.Match[str], KrokiImageContext | None]] = []
        for match_obj in matches:
            kroki_type = self.diagram_types.get_kroki_type(match_obj.group("lang"))
            if kroki_type is None:
                # Skip not supported code blocks
                match_data.append((match_obj, None))
                continue

            kroki_options = match_obj.group("opts")
            options = {}
            plugin_options = {}
            if kroki_options:
                # Strip curly braces if present and parse key=value pairs
                opts_str = kroki_options.strip().strip("{}")
                for x in opts_str.split():
                    if "=" in x and not x.startswith("kroki="):
                        key, value = x.split("=", 1)
                        if key in PLUGIN_OPTIONS:
                            plugin_options[key] = value
                        else:
                            options[key] = value

            kroki_context = KrokiImageContext(
                kroki_type=kroki_type,
                options=options,
                plugin_options=plugin_options,
                data=self._get_block_content(textwrap.dedent(match_obj.group("code"))),
            )
            match_data.append((match_obj, kroki_context))
            tasks.append(block_callback(kroki_context, context))

        # Run all async tasks
        async def _gather_tasks():
            return await asyncio.gather(*tasks)

        if tasks:
            results = asyncio.run(_gather_tasks())
        else:
            results = []

        # Build replacement map
        replacements: dict[tuple[int, int], str] = {}
        result_idx = 0
        for match, ctx in match_data:
            if ctx is None:
                # Not a kroki block, keep original
                replacements[match.span()] = match.group()
            else:
                # Use the async result
                replacements[match.span()] = textwrap.indent(
                    results[result_idx], match.group("indent")
                )
                result_idx += 1

        # Apply replacements in reverse order to maintain positions
        result = markdown
        for (start, end), replacement in sorted(replacements.items(), reverse=True):
            result = result[:start] + replacement + result[end:]

        return result
