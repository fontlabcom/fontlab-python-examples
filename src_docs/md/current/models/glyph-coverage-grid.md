---
this_file: src_docs/md/current/models/glyph-coverage-grid.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Coverage Grid

What: Inspect Unicode coverage as a sixteen-column grid of glyph names.
How: Group every captured Unicode assignment into rows of sixteen scalars.
Keep all names when several glyphs share a scalar. Leave absent cells blank.
Why: A name grid reveals gaps and collisions without substituting font previews.
Usage: Open a font and Refresh. Combine each row label with the column digit.
Copy or export JSON to record the complete coverage grid.
Benefit: Locate duplicate assignments and missing positions during font review.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Refresh stages results before replacing the visible grid.

Independent rewrite of the Qt pixelator example idea. Based on the author's own FontLab sample,
Apache-2.0.
Historical source: rescued/part2/ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py
SHA256: 9b8e6b6e8c542817876e897eef2d9d5a503c40eea8486dc6ef975621e123444c
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py
SHA256: dcffd1f6ddaf3cbbe1b72fa90816d42892ce5abccf5ff0098e7e5cc50c9270bb

Run **Models > Glyph Coverage Grid** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/47d32b422a4768f6a533854f33dffc10044493aad74b1196ceedbabcd1db9692.py)
<!--/codeinclude-->
