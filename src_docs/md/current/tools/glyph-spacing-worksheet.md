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
Original profile setup:
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


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Metrics Controls Lab; opens the Glyph Spacing Worksheet profile.

Run **Tools > Glyph Spacing Worksheet** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `7390079fc7caa5763e7633c7cdb470dc52aa7d6a2ef2809aeaf883456d40abd9`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Tools/Glyph%20Spacing%20Worksheet.py)
