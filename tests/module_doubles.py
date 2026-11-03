# this_file: tests/module_doubles.py
"""Install module doubles with the parent attributes Python dotted imports use."""

import sys
from types import ModuleType
from typing import Any


def install_module(monkeypatch: Any, name: str, module: Any) -> None:
    """Keep sys.modules and its package tree consistent, with pytest cleanup."""
    parent, _, child = name.rpartition(".")
    if parent:
        if parent not in sys.modules:
            package = ModuleType(parent)
            package.__path__ = []
            install_module(monkeypatch, parent, package)
        monkeypatch.setattr(sys.modules[parent], child, module, raising=False)
    monkeypatch.setitem(sys.modules, name, module)
