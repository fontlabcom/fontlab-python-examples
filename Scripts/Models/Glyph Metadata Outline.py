# this_file: Scripts/Models/Glyph Metadata Outline.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect all current-font glyph metadata in an expandable read-only hierarchy.

Purpose: Adapt the complete part2 Simple Tree Model workflow to FontLab.
Show glyphs in font order. Expand each glyph to inspect all Unicode assignments
and its local modification date. Missing values remain explicit.
Original profile setup: FontLab9 Python3.11, fontlab-fly and App>=0.2.57.dev0.
Run: Open a font and run this Models command. Expand or collapse rows; select a
cell to inspect it. Keep fixed columns, noneditable EditRole text, selected row/column status and File > Exit.
Use Refresh to read the current font again. Reads and rendering share a bounded
complete-snapshot budget. Failed reads clear the view and report the error.
Result: The complete metadata hierarchy is readable without changing the font.
Cells are never editable. Close releases models, selection owners and signals.
No font, native glyph selection, history, preferences or Output writer is called.
Design: Share generic immutable tree/model/lifetime code in App, through Fly.
Replace the synthetic outline/default.txt input with structured font metadata.
The separate editable-tree lesson remains outside this read-only source pair.
Compatibility: Uses FontLab's supplied PythonQt.
Historical source: rescued/part2/ports/itemviews/pyqt-official/simpletreemodel-321f8e535facafde.py
Original source/resources are archived outside this repository; this command does not execute them.


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Tree Models Lab; opens the Glyph Metadata Outline profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E02", profile='Glyph Metadata Outline')


if __name__ == "__main__":
    main()
