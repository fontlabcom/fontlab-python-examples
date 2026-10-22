---
this_file: src_docs/md/current/models/glyph-encoding-chart.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Encoding Chart

What: Find unencoded glyphs in the current font and measure encoding coverage.
How: Capture the complete App glyph catalogue. Count each glyph once, even when
it has several Unicode values. List each unencoded name on its own row after the exact totals.
Why: Counts show the scale of missing assignments; names identify the work.
Usage: Open a font, run this panel and Refresh. Copy or export the JSON report.
Benefit: Use the name list to plan encoding corrections without changing the font.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Close disconnects callbacks; Refresh failures keep prior results.

Independent rewrite of the Qt chart example idea. Based on the author's own FontLab sample,
Apache-2.0.
Historical source: rescued/part2/ports/itemviews/pyqt-official/chart-306c12d5cc1db46c.py
SHA256: 9e370ed256018c9b63db004c6693b85685a50169b7d7be45b9b5809d7ed37510
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/chart-306c12d5cc1db46c.py
SHA256: 0bdf280e85649088518dfc0647ad99a46ab7f446eac7b52aed2eee1d25912956

Run **Models > Glyph Encoding Chart** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/76318216ef05fc617a325d8417708e4b9b09d2733b37fdd8bac751e5980a1540.py)
<!--/codeinclude-->
