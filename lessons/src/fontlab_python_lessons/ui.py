# this_file: lessons/src/fontlab_python_lessons/ui.py
# SPDX-License-Identifier: Apache-2.0
"""Resolve native lesson classes lazily, inside the existing FontLab process."""
from typing import Any


def dialog_type(name: str) -> type[Any]:
    """Return the selected lesson class without constructing a QApplication."""
    if name == "glyph-metrics-form":
        from .form_dialog import GlyphMetricsForm
        return GlyphMetricsForm
    from .panels import GlyphMetricsModel, GlyphNameFilter
    return {"glyph-name-filter": GlyphNameFilter,
            "glyph-metrics-model": GlyphMetricsModel}[name]
