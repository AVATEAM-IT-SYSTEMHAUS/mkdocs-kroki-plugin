import os
import tempfile
from pathlib import Path

from kroki.cache import KrokiCache


def test_cache_stores_and_retrieves():
    """Test that cache can store and retrieve diagram content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = KrokiCache(cache_dir=tmpdir)

        diagram_source = "graph TD; A-->B;"
        diagram_type = "mermaid"
        file_ext = "svg"
        options = {}
        content = b"<svg>test diagram</svg>"

        # Store in cache
        cache.set(diagram_source, diagram_type, file_ext, options, content)

        # Retrieve from cache
        retrieved = cache.get(diagram_source, diagram_type, file_ext, options)

        assert retrieved == content


def test_cache_miss():
    """Test that cache returns None for non-existent entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = KrokiCache(cache_dir=tmpdir)

        retrieved = cache.get(
            diagram_source="graph TD; A-->B;",
            diagram_type="mermaid",
            file_ext="svg",
            options={},
        )

        assert retrieved is None


def test_cache_different_options():
    """Test that different options result in different cache entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = KrokiCache(cache_dir=tmpdir)

        diagram_source = "graph TD; A-->B;"
        diagram_type = "mermaid"
        file_ext = "svg"
        content1 = b"<svg>with option1</svg>"
        content2 = b"<svg>with option2</svg>"

        # Store with different options
        cache.set(diagram_source, diagram_type, file_ext, {"theme": "dark"}, content1)
        cache.set(diagram_source, diagram_type, file_ext, {"theme": "light"}, content2)

        # Retrieve should give different content
        retrieved1 = cache.get(
            diagram_source, diagram_type, file_ext, {"theme": "dark"}
        )
        retrieved2 = cache.get(
            diagram_source, diagram_type, file_ext, {"theme": "light"}
        )

        assert retrieved1 == content1
        assert retrieved2 == content2


def test_cache_memory_layer():
    """Test that in-memory cache is used for subsequent reads."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = KrokiCache(cache_dir=tmpdir)

        diagram_source = "graph TD; A-->B;"
        diagram_type = "mermaid"
        file_ext = "svg"
        options = {}
        content = b"<svg>test diagram</svg>"

        # Store in cache
        cache.set(diagram_source, diagram_type, file_ext, options, content)

        # First retrieval (from file)
        retrieved1 = cache.get(diagram_source, diagram_type, file_ext, options)

        # Second retrieval (should be from memory)
        retrieved2 = cache.get(diagram_source, diagram_type, file_ext, options)

        assert retrieved1 == content
        assert retrieved2 == content


def test_cache_persistence():
    """Test that cache persists across cache instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        diagram_source = "graph TD; A-->B;"
        diagram_type = "mermaid"
        file_ext = "svg"
        options = {}
        content = b"<svg>test diagram</svg>"

        # Store with first cache instance
        cache1 = KrokiCache(cache_dir=tmpdir)
        cache1.set(diagram_source, diagram_type, file_ext, options, content)

        # Retrieve with second cache instance
        cache2 = KrokiCache(cache_dir=tmpdir)
        retrieved = cache2.get(diagram_source, diagram_type, file_ext, options)

        assert retrieved == content


def test_cache_uses_xdg_cache_home(monkeypatch):
    """Test that cache uses XDG_CACHE_HOME when set."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("XDG_CACHE_HOME", tmpdir)

        cache = KrokiCache()

        expected_path = Path(tmpdir) / "kroki"
        assert cache.cache_path == expected_path
        assert expected_path.exists()


def test_cache_falls_back_to_home_cache(monkeypatch):
    """Test that cache falls back to ~/.cache/kroki when XDG_CACHE_HOME is not set."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        monkeypatch.setenv("HOME", tmpdir)

        cache = KrokiCache()

        expected_path = Path(tmpdir) / ".cache" / "kroki"
        assert cache.cache_path == expected_path
        assert expected_path.exists()


def test_cache_file_naming():
    """Test that cache files are created with correct naming."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = KrokiCache(cache_dir=tmpdir)

        diagram_source = "graph TD; A-->B;"
        diagram_type = "mermaid"
        file_ext = "svg"
        options = {}
        content = b"<svg>test diagram</svg>"

        cache.set(diagram_source, diagram_type, file_ext, options, content)

        # Check that a file with .svg extension was created
        cache_files = list(Path(tmpdir).glob("*.svg"))
        assert len(cache_files) == 1
        assert cache_files[0].read_bytes() == content


def test_cache_falls_back_to_temp(monkeypatch):
    """Test that cache falls back to temp directory when XDG_CACHE_HOME and HOME are not set."""
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.delenv("HOME", raising=False)

    cache = KrokiCache()

    # Should use temp directory
    assert cache.cache_path is not None
    assert str(cache.cache_path).startswith(tempfile.gettempdir())
    assert cache.cache_path.name == "kroki"


def test_cache_cleanup_old_files():
    """Test that old cache files are cleaned up on initialization."""
    import time

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir)

        # Create an old cache file (4 days old, should be deleted)
        old_file = cache_dir / "old_diagram.svg"
        old_file.write_bytes(b"<svg>old</svg>")
        # Set modification time to 4 days ago
        old_time = time.time() - (4 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))

        # Create a recent cache file (1 day old, should be kept)
        recent_file = cache_dir / "recent_diagram.svg"
        recent_file.write_bytes(b"<svg>recent</svg>")
        # Set modification time to 1 day ago
        recent_time = time.time() - (1 * 24 * 60 * 60)
        os.utime(recent_file, (recent_time, recent_time))

        # Initialize cache, which should trigger cleanup
        _ = KrokiCache(cache_dir=tmpdir)

        # Old file should be deleted
        assert not old_file.exists()
        # Recent file should still exist
        assert recent_file.exists()


def test_cache_touches_file_on_read():
    """Test that cache updates file modification time when reading (LRU strategy)."""
    import time

    with tempfile.TemporaryDirectory() as tmpdir:
        cache = KrokiCache(cache_dir=tmpdir)

        diagram_source = "graph TD; A-->B;"
        diagram_type = "mermaid"
        file_ext = "svg"
        options = {}
        content = b"<svg>test diagram</svg>"

        # Store in cache
        cache.set(diagram_source, diagram_type, file_ext, options, content)

        # Get the cache file path
        cache_files = list(Path(tmpdir).glob("*.svg"))
        assert len(cache_files) == 1
        cache_file = cache_files[0]

        # Get initial modification time
        initial_mtime = cache_file.stat().st_mtime

        # Wait a bit to ensure time difference
        time.sleep(0.1)

        # Read from cache (should touch the file)
        # Clear in-memory cache first to force file read
        cache.in_memory_cache.clear()
        retrieved = cache.get(diagram_source, diagram_type, file_ext, options)

        assert retrieved == content

        # Modification time should be updated
        new_mtime = cache_file.stat().st_mtime
        assert new_mtime > initial_mtime
