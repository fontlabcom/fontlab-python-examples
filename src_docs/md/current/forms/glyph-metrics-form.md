---
this_file: src_docs/md/current/forms/glyph-metrics-form.md
tags: ["Forms"]
categories: ["Forms"]
---

# Glyph Metrics Form

Load a Designer form and compare a hypothetical real-glyph advance.

Open a font and run this Forms menu entry. Choose a glyph from its actual names.
Read its current-master advance and left sidebearing. Enter a hypothetical
advance and click Preview Difference. The result compares plain values only;
there is no Apply command and no font data is written. Refresh adopts current
font data. Changed fonts, masters or displayed metrics refuse stale previews.

Install fontlab-python-lessons and its fly/App dependencies in FontLab's
Python3.11 environment. The packaged .ui stays outside the Scripts menu. Its
known controls, file handles, signal callbacks and window have explicit owners.

Run **Forms > Glyph Metrics Form** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/552075cdbe2d26d4f36360447ffa1bba09973a4a24a4580cda0ef6ed5b987ae5.py)
<!--/codeinclude-->
