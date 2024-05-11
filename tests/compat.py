import sys

# backport chdir context manager
if sys.version_info < (3, 11):
    import os
    from contextlib import AbstractContextManager

    class chdir(AbstractContextManager):  # noqa: N801
        """Non thread-safe context manager to change the current working directory."""

        def __init__(self, path):
            self.path = path
            self._old_cwd = []

        def __enter__(self):
            self._old_cwd.append(os.getcwd())
            os.chdir(self.path)

        def __exit__(self, *excinfo):
            os.chdir(self._old_cwd.pop())
else:
    from contextlib import chdir  # noqa: F401
