# this_file: Scripts/Models/Glyph Name Filter.py
# SPDX-License-Identifier: Apache-2.0
"""Filter real glyph names with a Qt list model, then select chosen results.

Open a font and run this script from Models in FontLab's Scripts menu. Enter a
prefix and click Apply Prefix. Choose rows, then click Select Chosen Rows to
change Font window selection. Refresh reads a new font/master/name snapshot.
The panel refuses stale results. It never changes glyph data or preferences.

Install fontlab-python-lessons, fontlab-fly and fontlab-fontlabapp in FontLab's
Python3.11 environment. The package uses fly.ap for shared native access and
owned signal/window cleanup. This keeps the lesson focused on list models.
"""
from fontlab_python_lessons import launch

if __name__ == "__main__":
    launch("glyph-name-filter")
