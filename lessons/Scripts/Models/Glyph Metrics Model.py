# this_file: lessons/Scripts/Models/Glyph Metrics Model.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect real selected-glyph metrics with a read-only Qt table model.

Select glyphs in FontLab's Font window, then run this Models menu entry. The
table shows their current-master names, advances and outline left sidebearings
in font order. Zero remains zero; an em dash marks unavailable layer/outline
data. Refresh explicitly reads the current selection and master after edits.

No glyph fallback or edit occurs. Install fontlab-python-lessons and its fly/App
dependencies in FontLab's Python3.11 environment. Shared fly.ap lifetime helpers
keep the modeless panel owned and disconnect callbacks before destruction.
"""
from fontlab_python_lessons import launch

if __name__ == "__main__":
    launch("glyph-metrics-model")
