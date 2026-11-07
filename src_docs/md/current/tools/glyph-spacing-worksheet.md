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
    Independent behavior implementation; no preserved body/helper is executed.
    Historical source: rescued/part2/ports/itemviews/pyqt-official/spinboxdelegate-ddb20b1b68b18a91.py

Run **Tools > Glyph Spacing Worksheet** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `c81ed034fd57ffedd415f0958fc10008f463ff392703afe5d0badc7a6f2f6749`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Tools/Glyph%20Spacing%20Worksheet.py)
