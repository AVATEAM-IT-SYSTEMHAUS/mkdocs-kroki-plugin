import re
import textwrap
from collections.abc import Callable
from pathlib import Path
from typing import Final

from result import Err, Ok, Result

from kroki.common import ErrorResult, KrokiImageContext, MkDocsEventContext
from kroki.diagram_types import KrokiDiagramTypes
from kroki.logging import log


class MarkdownParser:
    from_file_prefix: Final[str] = "@from_file:"
    _FENCE_RE = re.compile(
        r"(?P<fence>^(?P<indent>[ ]*)(?:````*|~~~~*))[ ]*"
        r"(\.?(?P<lang>[\w#.+-]*)[ ]*)?"
        r"(?P<opts>(?:[ ]?[a-zA-Z0-9\-_]+=[a-zA-Z0-9\-_]+)*)\n"
        r"(?P<code>.*?)(?<=\n)"
        r"(?P=fence)[ ]*$",
        flags=re.IGNORECASE + re.DOTALL + re.MULTILINE,
    )

    def __init__(self, docs_dir: str, diagram_types: KrokiDiagramTypes) -> None:
        self.diagram_types = diagram_types
        self.docs_dir = docs_dir

    def _get_block_content(self, block_data: str) -> Result[str, ErrorResult]:
        if not block_data.startswith(self.from_file_prefix):
            return Ok(block_data)

        file_name = block_data.removeprefix(self.from_file_prefix).strip()
        file_path = Path(self.docs_dir) / file_name
        log.debug('Reading kroki block from file: "%s"', file_path.absolute())
        try:
            with open(file_path) as data_file:
                return Ok(data_file.read())
        except OSError as error:
            return Err(
                ErrorResult(
                    err_msg=f'Can\'t read file: "{file_path.absolute()}" from code block "{block_data}"', error=error
                )
            )

    def replace_kroki_blocks(
        self,
        markdown: str,
        block_callback: Callable[[KrokiImageContext, MkDocsEventContext], str],
        context: MkDocsEventContext,
    ) -> str:
        def replace_kroki_block(match_obj: re.Match):
            kroki_type = self.diagram_types.get_kroki_type(match_obj.group("lang"))
            if kroki_type is None:
                # Skip not supported code blocks
                return match_obj.group()

            kroki_options = match_obj.group("opts")
            kroki_context = KrokiImageContext(
                kroki_type=kroki_type,
                options=dict(x.split("=") for x in kroki_options.strip().split(" ")) if kroki_options else {},
                data=self._get_block_content(textwrap.dedent(match_obj.group("code"))),
            )
            return textwrap.indent(block_callback(kroki_context, context), match_obj.group("indent"))

        return re.sub(self._FENCE_RE, replace_kroki_block, markdown)
