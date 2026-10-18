# this_file: src/fontlab_python_lessons/__init__.py
# SPDX-License-Identifier: Apache-2.0
"""Run three useful FontLab UI lessons without importing the host eagerly.

Install this package and its fly/App dependencies in FontLab's Python 3.11.
Copy the distributed Scripts folder into a Scripts search path. Each menu entry
opens one modeless lesson. Importing this package outside FontLab is supported;
launching requires the existing application and its PythonQt binding.
"""
from importlib.metadata import PackageNotFoundError, version
from typing import Any

try:
    __version__ = version("fontlab-python-lessons")
except PackageNotFoundError:
    __version__ = "0+uninstalled"


def launch(name: str) -> Any:
    """Open a named lesson; replace only its previous owned dialog.

    Names are glyph-name-filter, glyph-metrics-model and glyph-metrics-form.
    Native imports occur here, after the caller explicitly requests a window.
    """
    names = ("glyph-name-filter", "glyph-metrics-model", "glyph-metrics-form")
    if name not in names:
        raise ValueError(f"Unknown lesson {name!r}; choose {', '.join(names)}.")
    from fly.ap.scripting import show_script_dialog

    from .ui import dialog_type

    return show_script_dialog(dialog_type(name), "examples-" + name)
