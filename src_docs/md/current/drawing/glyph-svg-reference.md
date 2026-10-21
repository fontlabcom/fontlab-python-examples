---
this_file: src_docs/md/current/drawing/glyph-svg-reference.md
tags: ["Drawing"]
categories: ["Drawing"]
---

# Glyph SVG Reference

What: Compare local SVG reference artwork with the current glyph outline.
How: Read the current-master outline and load the whole SVG into a native vector
scene item. Fit and center it, or keep SVG user coordinates in font units.
Draw the glyph in blue above the translucent reference. No SVG bytes are changed.
Why: Compare silhouettes without rasterizing the reference or changing the font.
Usage: Open a glyph. Enter an absolute SVG path and click Compare. Opacity
updates the loaded reference. Compare again after font changes.
Benefit: See proportion differences while designing a glyph in FontLab.
Fit mode normalizes silhouettes. Font units mode keeps SVG user coordinates:
x increases right, y increases downward, and the glyph baseline is y=0.
Neither mode checks imported font metrics.
Animated SVG is refused. Rendering uses the SVG features supported by host Qt.
Setup: FontLab 9, Python 3.11, Fly, fontlabapp and QtSvg.QGraphicsSvgItem.
Independent rewrite of the Qt svgviewer example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.

Run **Drawing > Glyph SVG Reference** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/41d5f3224ee0ea6138e3dfbb0682927669a656b1560377d0cadff3526a0f7098.py)
<!--/codeinclude-->
