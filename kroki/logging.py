from typing import Final

from mkdocs.plugins import get_plugin_logger

log = get_plugin_logger(__name__)

_COLOR_PURPLE: Final[str] = "\x1b[35;1m"
_COLOR_RESET: Final[str] = "\x1b[0m"

log.prefix = f"{_COLOR_PURPLE}{log.prefix}{_COLOR_RESET}"
