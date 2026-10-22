---
this_file: src_docs/md/current/graphics/glyph-proof-pad.md
tags: ["Graphics"]
categories: ["Graphics"]
---

# Glyph Proof Pad

What: Browse the current font as a nine-cell proof-name pad.
How: Capture glyph names once. Previous and Next change the page. Click a
named cell to prepare its exact slash name; Copy Result transfers the text.
Why: Unencoded glyphs also need reliable proof-text access.
Usage: Enter a glyph-name prefix, then Refresh after font changes. Use Previous/Next (Alt+Left/Alt+Right),
click a cell, then Copy Result and paste in a Glyph window text bar.
Benefit: Build proof input without changing the Font window selection.
Only current-font names appear; the UI does not use system-font substitutes.
The original OpenGL viewport and animation are replaced by plain Qt widgets.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt padnavigator example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Historical source: rescued/part2/ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py
SHA256: 66f7c5169c23e0adb6a7cb76b9fdffbf33b27af79bc987cafb8534365d70632d
Historical source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py
SHA256: f6af280b00f13384566780930eb7aa33b57c5202a933315841d946fcf79cfe07

Run **Graphics > Glyph Proof Pad** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/157a461e60c5ec8c50d019463b7e94a0a56e28517b06758d28248f9d5fd41f3e.py)
<!--/codeinclude-->
