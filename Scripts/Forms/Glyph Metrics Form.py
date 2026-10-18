# this_file: Scripts/Forms/Glyph Metrics Form.py
# SPDX-License-Identifier: Apache-2.0
"""Load a Designer form and compare a hypothetical real-glyph advance.

Open a font and run this Forms menu entry. Choose a glyph from its actual names.
Read its current-master advance and left sidebearing. Enter a hypothetical
advance and click Preview Difference. The result compares plain values only;
there is no Apply command and no font data is written. Refresh adopts current
font data. Changed fonts, masters or displayed metrics refuse stale previews.

Install fontlab-python-lessons and its fly/App dependencies in FontLab's
Python3.11 environment. The packaged .ui stays outside the Scripts menu. Its
known controls, file handles, signal callbacks and window have explicit owners.
"""
from fontlab_python_lessons import launch

if __name__ == "__main__":
    launch("glyph-metrics-form")
