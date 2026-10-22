---
this_file: src_docs/md/current/models/glyph-mark-colours.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Mark Colours

What: Edit glyph mark colours in a table of the current FontLab font.
How: Capture scalar glyph identities and marks through App names_edit. Each
colour cell uses a combo delegate with FontLab hue and grey presets. Apply
rechecks the current font and original values, then calls App history.commit
with metadata policy for only changed rows. One Apply creates one Undo step.
Why: Native marks persist with the font and support FontLab colour selection.
Usage: Open a font, double-click colour cells, choose marks and click Apply.
Use Discard Changes to restore local edits. Glyphs with auto layers are
refused.
Benefit: Review many glyph marks without changing names, notes or outlines.
Requires: FontLab 9, Python 3.11, Fly and App names_edit, history,
draft_signals
and qt_properties. Failed writes retain the local plan and show Undo guidance.

Independent rewrite of the Qt coloreditorfactory example idea. Based on the
author's own FontLab sample,
Apache-2.0.
Historical source: rescued/part2/ports/itemviews/pyqt-official/coloreditorfactory-0a3b15766909bdc3.py
SHA256: 06780068bb97fb0b0787dbc5fc5dc5d51b1c2c29cfd053fa0ba6be4be802ce58
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/coloreditorfactory-0a3b15766909bdc3.py
SHA256: 5b4aa3c5c7aaad2b40cb25c868c6aa41f828dbc884021db9fd2d630f5cd64534

Run **Models > Glyph Mark Colours** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/db00c97f22db69cea682111a5ea7ddce7e525287375a24b35b42555db1f7e27a.py)
<!--/codeinclude-->
