import hashlib
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

from kroki.logging import log


def _determine_cache_dir(custom_dir: Optional[str]) -> Path:
    """Determine the cache directory with fallback hierarchy."""
    if custom_dir:
        return Path(custom_dir)

    # Try XDG_CACHE_HOME
    xdg_cache = os.getenv("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / "kroki"

    # Try HOME/.cache
    home = os.getenv("HOME")
    if home:
        return Path(home) / ".cache" / "kroki"

    # Fall back to temp directory
    tmpdir = os.getenv("TMPDIR", tempfile.gettempdir())
    log.info("Using temporary directory for cache: %s", tmpdir)
    return Path(tmpdir) / "kroki"


def _get_cache_key(
    diagram_source: str, diagram_type: str, file_ext: str, options: dict
) -> str:
    """Generate a cache key based on diagram content and metadata.

    Args:
        diagram_source: The diagram source code
        diagram_type: The type of diagram (e.g., 'mermaid', 'plantuml')
        file_ext: The file extension (e.g., 'svg', 'png')
        options: Diagram rendering options

    Returns:
        A hex string cache key
    """
    # Sort options to ensure consistent hashing
    sorted_options = sorted(options.items())
    cache_data = f"{diagram_type}:{file_ext}:{diagram_source}:{sorted_options}"
    return hashlib.sha256(cache_data.encode()).hexdigest()


class KrokiCache:
    """Manages caching of rendered diagrams to avoid re-rendering unchanged diagrams.

    Uses an access-time based LRU strategy: files are touched on read,
    and old unused files are cleaned up on initialization.
    """

    # Cache TTL in seconds (3 days)
    CACHE_TTL_SECONDS = 3 * 24 * 60 * 60

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        """Initialize the cache.

        Args:
            cache_dir: Optional custom cache directory. If None, uses fallback hierarchy:
                       1. $XDG_CACHE_HOME/kroki
                       2. $HOME/.cache/kroki
                       3. $TMPDIR/kroki or temp directory/kroki
        """
        self.in_memory_cache: dict[str, bytes] = {}
        self.cache_path: Path | None = _determine_cache_dir(cache_dir)
        log.debug("Using cache directory: %s", self.cache_path)
        self._ensure_cache_dir()
        self._cleanup_old_cache_files()

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        if self.cache_path:
            try:
                self.cache_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                log.warning(
                    "Could not create cache directory %s: %s", self.cache_path, e
                )
                self.cache_path = None

    def _cleanup_old_cache_files(self) -> None:
        """Remove cache files that haven't been accessed in CACHE_TTL_SECONDS."""
        if not self.cache_path or not self.cache_path.exists():
            return

        try:
            current_time = time.time()
            cutoff_time = current_time - self.CACHE_TTL_SECONDS
            deleted_count = 0

            for cache_file in self.cache_path.iterdir():
                if not cache_file.is_file():
                    continue

                try:
                    # Check modification time (last access time when we touch files)
                    mtime = cache_file.stat().st_mtime
                    if mtime < cutoff_time:
                        cache_file.unlink()
                        deleted_count += 1
                except Exception as e:
                    log.debug("Could not delete cache file %s: %s", cache_file, e)

            if deleted_count > 0:
                log.info("Cleaned up %d old cache files", deleted_count)

        except Exception as e:
            log.warning("Error during cache cleanup: %s", e)

    def get(
        self, diagram_source: str, diagram_type: str, file_ext: str, options: dict
    ) -> Optional[bytes]:
        """Retrieve cached diagram if it exists.

        Args:
            diagram_source: The diagram source code
            diagram_type: The type of diagram
            file_ext: The file extension
            options: Diagram rendering options

        Returns:
            Cached diagram content as bytes, or None if not cached
        """
        cache_key = _get_cache_key(diagram_source, diagram_type, file_ext, options)

        # Check in-memory cache first
        if cache_key in self.in_memory_cache:
            log.debug("Cache hit (memory): %s", cache_key[:16])
            return self.in_memory_cache[cache_key]

        # Check file cache
        if self.cache_path:
            cache_file = self.cache_path / f"{cache_key}.{file_ext}"
            if cache_file.exists():
                try:
                    content = cache_file.read_bytes()
                    # Touch file to update access time (LRU strategy)
                    try:
                        cache_file.touch()
                    except Exception:
                        pass  # Ignore touch errors, not critical
                    # Store in memory cache for faster future access
                    self.in_memory_cache[cache_key] = content
                    log.debug("Cache hit (file): %s", cache_key[:16])
                    return content
                except Exception as e:
                    log.warning("Could not read cache file %s: %s", cache_file, e)

        log.debug("Cache miss: %s", cache_key[:16])
        return None

    def set(
        self,
        diagram_source: str,
        diagram_type: str,
        file_ext: str,
        options: dict,
        content: bytes,
    ) -> None:
        """Store diagram in cache.

        Args:
            diagram_source: The diagram source code
            diagram_type: The type of diagram
            file_ext: The file extension
            options: Diagram rendering options
            content: The rendered diagram content
        """
        cache_key = _get_cache_key(diagram_source, diagram_type, file_ext, options)

        # Always store in memory cache
        self.in_memory_cache[cache_key] = content

        # Store in file cache if available
        if self.cache_path:
            cache_file = self.cache_path / f"{cache_key}.{file_ext}"
            try:
                cache_file.write_bytes(content)
                log.debug("Cached to file: %s", cache_key[:16])
            except Exception as e:
                log.warning("Could not write cache file %s: %s", cache_file, e)
