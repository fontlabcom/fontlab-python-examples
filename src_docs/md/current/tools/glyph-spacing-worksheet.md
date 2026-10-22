---
this_file: src_docs/md/current/tools/glyph-spacing-worksheet.md
tags: ["Tools"]
categories: ["Tools"]
---

# Glyph Spacing Worksheet

Compare four local spacing recipes against every selected glyph-layer advance.

Purpose:
    Keep the complete preserved part2 Spin Box Delegate lesson useful in FontLab.
    A is a font-unit increment. B is its repeat count. Edit all eight cells.
Setup:
    Use FontLab 9, Python 3.11, Fly and App>=0.2.70.dev0.
    Use matching artifacts. No automatic installation is performed.
Run:
    Select glyph layers, then open this modeless worksheet from Tools.
    Edit factors even without a font. Refresh Selection reads a complete snapshot.
    Reset Factors restores original values and types. Close cancels pending input.
Result:
    Read each captured baseline and all four baseline-plus-A-times-B candidates.
    Candidates change no font metrics. Failed refresh retains the prior report.
Compatibility:
    Native PythonQt and complete font/cache/history/reopen acceptance are pending.
    Independent behavior implementation; no preserved body/helper is executed.
    Historical source: rescued/part2/ports/itemviews/pyqt-official/spinboxdelegate-ddb20b1b68b18a91.py

Run **Tools > Glyph Spacing Worksheet** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/354fa6c78e1297a601af54cf3e719da700345b15565d4cd866ec49f907d427b7.py)
<!--/codeinclude-->
