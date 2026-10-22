---
this_file: src_docs/md/current/graphics/glyph-mark-colour-board.md
tags: ["Graphics"]
categories: ["Graphics"]
---

# Glyph Mark Colour Board

What: Drop colour swatches onto prefix-matched glyphs to set FontLab marks.
How: Capture current-font glyph identities. A drop makes one metadata Undo step
through App history. Read-back checks individually coloured layer overrides.
Native glyph-to-layer mark propagation is unverified.
Why: Organize a review group with visible glyph marks in the Font window.
Usage: Enter a glyph-name prefix, Refresh, then drag a swatch onto a tile.
Refresh after changing the font or master. None clears the glyph's mark.
Benefit: Flag individual glyphs directly without changing the font selection.
The table and selection swatches edit the same property; this board adds
prefix-scoped, drag-and-drop editing.
Glyphs with auto layers are refused. A partial write reports Edit > Undo.
Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; each drop edits one glyph.
Independent rewrite of the Qt dragdroprobot example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Historical source: rescued/part2/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py
SHA256: f1faf59693b2054c207de5811e7d721260755e6a5675f199f3472e3d520204d2
Historical source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py
SHA256: c021aba5ca45ca9cf3b0fde77ceb654ff5077191380d83cef5d84c1aec9c8313

Run **Graphics > Glyph Mark Colour Board** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/34e562975a08072aff30b900b2bef0c551f4c7d1e7f344332bb4a3513a5140bb.py)
<!--/codeinclude-->
