---
this_file: src_docs/md/current/models/glyph-metadata-outline.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Metadata Outline

Inspect all current-font glyph metadata in an expandable read-only hierarchy.

Purpose: Adapt the complete part2 Simple Tree Model workflow to FontLab.
Show glyphs in font order. Expand each glyph to inspect all Unicode assignments
and its local modification date. Missing values remain explicit.
Setup: FontLab9 Python3.11, fontlab-fly and App>=0.2.57.dev0.
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

Run **Models > Glyph Metadata Outline** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/96fe704f5e47a73b3c68185030d32028d670c1c136bbf83c5e91e1218f427e01.py)
<!--/codeinclude-->
