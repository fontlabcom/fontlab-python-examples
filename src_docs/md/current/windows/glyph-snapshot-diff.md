---
this_file: src_docs/md/current/windows/glyph-snapshot-diff.md
tags: ["Windows"]
categories: ["Windows"]
---

# Glyph Snapshot Diff

What: Compare the first captured glyph catalogue with the newest capture.
How: Bind both snapshots to the current font package. Match glyph names and
compare complete Unicode sets plus modification dates and epoch milliseconds.
Report added, removed, re-encoded and modified glyphs in separate change rows.
Why: A focused difference is easier to review than two complete inventories.
Usage: Run to capture the baseline. Make changes in FontLab, then Capture Latest.
The first capture stays fixed. Reset Baseline explicitly starts a new comparison,
including after switching fonts. Previous and Next page the display; Copy All Diff
copies the complete comparison. Renames appear as a removed and an added glyph.
A glyph can be both re-encoded and modified. Unicode order alone is not a change.
Benefit: Review the actual effects of a script or manual edit, with every changed
Unicode and modification value retained. This tool changes no font data.
Setup: FontLab 9, Python 3.11, Fly and App with glyph_catalog, scripting,
draft_signals. The modeless window contains one reusable table.
Independent rewrite of the Qt mdi example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.

Historical source: rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/mdi-1415facde30a25cf.py
SHA256: 29271121483f2c5fabe6b0f0232602bcc32f9d0a0ccc69ad553149a5706d8199
Historical source: rescued/part2/ports/mainwindows/pyqt-official/mdi-1415facde30a25cf.py
SHA256: 4a7cab42d4c0c13dd09e5c098e6758007f81371fbb90b832d25c1f44e055609c

Run **Windows > Glyph Snapshot Diff** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4c86e776454e86fec9b690bdc7395f4b94a8df2ae97c83822594878f0502fc87.py)
<!--/codeinclude-->
