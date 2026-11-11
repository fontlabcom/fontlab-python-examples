---
this_file: src_docs/md/current/tools/glyph-spacing-worksheet-frameless.md
tags: ["Tools"]
categories: ["Tools"]
---

# Glyph Spacing Worksheet - Frameless

Compare four local spacing recipes against every selected glyph-layer advance.

Purpose:
    Keep the complete preserved part3 Spin Box Delegate lesson useful in FontLab.
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
    Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/spinboxdelegate-ddb20b1b68b18a91.py


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Metrics Controls Lab; opens the Glyph Spacing Worksheet - Frameless profile.

Run **Tools > Glyph Spacing Worksheet - Frameless** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `fc8f343b66aa376af2242fd87336bf5228d05bbd4096bc9800d1cd4a5099bf49`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Tools/Glyph%20Spacing%20Worksheet%20-%20Frameless.py)
