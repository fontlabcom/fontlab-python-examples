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
Compatibility: Original PythonQt virtual/UI/getter/cache/font/history/save/reopen
acceptance remains pending. Standalone Qt is not native FontLab proof.
Historical source: rescued/part2/ports/itemviews/pyqt-official/simpletreemodel-321f8e535facafde.py
Original source/resources are archived outside this repository; this command does not execute them.

Run **Models > Glyph Metadata Outline** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0a2c7cb46bc2ef0f90cd721b0a612541b435ed9984e2f249888d2a889d3b24ca.py)
<!--/codeinclude-->
