# this_file: Scripts/Models/Glyph Metadata Tree.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 0eb40bcaded0341ad05f3891e54ee5f06e02616d3efa03b175742863d178fc86
"""Inspect all current-font glyph metadata in an expandable read-only hierarchy.

Purpose: Adapt the complete part3 Simple Tree Model workflow to FontLab.
Show glyphs in font order. Expand each glyph to inspect all Unicode assignments
and its local modification date. Missing values remain explicit.
Setup: FontLab9 Python3.11, fontlab-fly and reviewed unpublished App>=0.2.57.dev0.
Run: Open a font and run this Models command. Expand or collapse rows; select a
cell to inspect it. Keep DisplayRole-only text and parent-item column counts; no original selection-status control is added.
Use Refresh to read the current font again. Reads and rendering share a bounded
complete-snapshot budget. Failed reads clear the view and report the error.
Result: The complete metadata hierarchy is readable without changing the font.
Cells are never editable. Close releases models, selection owners and signals.
No font, native glyph selection, history, preferences or Output writer is called.
Design: Share generic immutable tree/model/lifetime code in App, through Fly.
Replace the synthetic outline/default.txt input with structured font metadata.
The separate editable-tree lesson remains outside this read-only source pair.
Compatibility: Original PythonQt virtual/UI/getter/cache/font/history/save/reopen
acceptance remains pending. Standalone Qt is not native FontLab proof.
Original: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/simpletreemodel-321f8e535facafde.py
Original source/resources stay preserved; this command does not execute them.
"""


def main() -> None:
    """Open the complete owned read-only hierarchy through the lazy Fly alias."""
    from fly.ap.glyph_tree import show_tree

    show_tree()


if __name__ == "__main__":
    main()
