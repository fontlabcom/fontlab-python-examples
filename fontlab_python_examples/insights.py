# this_file: fontlab_python_examples/insights.py
"""Build owned insight windows with rollback and explicit wrapper release."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fontlab_python_examples.handle import ExampleHandle


@contextmanager
def owned(window: Any, title: str) -> Iterator[ExampleHandle]:
    """Close a partial build on failure; drop retained children before deletion."""
    handle = ExampleHandle(window, dict)
    try:
        window.setWindowTitle(title)
        window.resize(420, 280)
        yield handle
    except BaseException:
        handle.close()
        raise
