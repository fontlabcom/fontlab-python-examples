---
this_file: src_docs/md/current/models/glyph-proof-worksheet.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Proof Worksheet

What: Calculate repeated FontLab slash-name proof lines for captured glyphs.
How: Keep one count per glyph. Apply Draft updates only that row's count and
proof items in the existing model. Refuse invalid counts and excessive output.
Why: Slash names retain alternate and unencoded glyph identities in proof text.
Usage: Open a font and Refresh. Choose a row, enter 1 to 1000 and Apply Draft.
Copy or Export New to use the proof in a Glyph window text bar. Export before
closing, or choose Discard and Close. Reset Draft explicitly discards changes.
Benefit: Prepare repeated spacing checks without typing each glyph occurrence.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Failed captures retain the current proof and pending count.

Independent rewrite of the Qt spreadsheet example idea. Based on the author's own FontLab sample,
Apache-2.0.
Source: rescued/part2/ports/itemviews/pyqt-official/spreadsheet-bf3b39a8c2df8e94.py
SHA256: b491650437d8faa9b59a6f4859bdb420c8507e4fde37fecc95ef87e7d0a2cd1d
Source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/spreadsheet-bf3b39a8c2df8e94.py
SHA256: 09ded2c0d8220569aadaa24f61bc7adc08c771ec364b6a1c6ef7d47ef76fddf7

Run **Models > Glyph Proof Worksheet** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/27ae99d2ffca349e67666aa071a0fa8ba639134375e21d96899f5e57b47dc577.py)
<!--/codeinclude-->
