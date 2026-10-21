---
this_file: src_docs/md/current/designer/em-star-polygon.md
tags: ["Designer"]
categories: ["Designer"]
---

# Em Star Polygon

What: Draw a star polygon in the current FontLab layer as one Undo step.
How: Alternate radii in font units, with Y up. Centre the contour on half the
active layer advance and half its associated master's FontMetrics cap height.
Why: Start ornamental glyphs from repeatable, font-sized construction.
Usage: Open a glyph. Set tips, radii in ems and rotation. Generate Preview,
then Draw in Current Layer. Each Draw adds one closed contour in a new shape.
Auto layers and bases of auto composites are refused. Read-back checks the
new contour and verifies every pre-existing shape's geometry. Layers without an
associated master are refused. Draw coordinates use whole-unit half-up rounding
(ties away from zero); read-back allows 0.5 units on each new-node coordinate.
A partial-write error directs you to Edit > Undo.
Benefit: Create geometric artwork directly in the active glyph layer.

The read-only shape preview is centred at the origin; drawing placement uses
the current advance and cap height. Equal radii produce a regular polygon with
twice the tip count. Positive rotation turns counterclockwise.
SVG is secondary output for an external vector editor. Generate Preview, then
copy the SVG text or Save New SVG to a new absolute .svg path. SVG uses a
Y-down em square and contains no font metrics, anchors or hints.
Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless panel.
The App panel owns signals and completion. No painter or plugin is needed.

Independent rewrite of the Qt polygonwidget example idea, David Boddie and
Trolltech ASA. Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.

Run **Designer > Em Star Polygon** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/fb8ee1b38ee27730dd58877bbb8ec9dbf2bdaef5c353384194497433f0b7de2f.py)
<!--/codeinclude-->
