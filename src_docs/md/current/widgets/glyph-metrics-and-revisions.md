---
this_file: src_docs/md/current/widgets/glyph-metrics-and-revisions.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Glyph Metrics and Revisions

Compare captured glyph metrics and revision cutoffs with local numeric drafts.

Purpose:
    Estimate advance offsets and scaled widths for every selected glyph layer.
    Inspect whole-font modification-date cutoffs and a per-glyph proof quote.
Original profile setup:
    Use FontLab 9, Python 3.11, Fly and App>=0.2.90.dev0.
    Open a font and select glyph layers. This script installs nothing.
Run:
    Edit the integer/decimal offsets, proof zoom, scale and currency estimates.
    Change precision to round the three local doubles. Change the independent
    date/time/instant cutoffs and instant format to inspect revision counts.
    Refresh captures the complete current selection and whole-font revisions;
    it preserves your inputs. Capture failure clears every stale result.
Result:
    Read both candidate advances in font units and the 12pt proof widths in pt.
    Quotes charge each distinct selected glyph once. Widths omit kerning and
    shaping. Close or Escape releases only this owned nonmodal worksheet.
Compatibility:
    This is retained spinboxes part2. Historical ranges and special zero
    semantics remain where the original defines them. Date/time controls
    filter local captured revision instants; they never change font dates.
    All numeric inputs are local estimates. No font/history/selection writer
    is used.
    Historical source: rescued/part2/ports/widgets/pyqt-official/spinboxes-468179092748a72e.py


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Metrics Controls Lab; opens the Glyph Metrics and Revisions profile.

Run **Widgets > Glyph Metrics and Revisions** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `2ef5da3dbec3a28265181a480a8563cd98c3267eaf3cf13ca100d78d7c6f3b1b`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Widgets/Glyph%20Metrics%20and%20Revisions.py)
