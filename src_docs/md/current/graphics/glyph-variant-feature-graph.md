---
this_file: src_docs/md/current/graphics/glyph-variant-feature-graph.md
tags: ["Graphics"]
categories: ["Graphics"]
---

# Glyph Variant Feature Graph

What: Show directed base-to-variant relationships for the current font.
How: Match an exact final suffix such as alt or ss01. Draw each base -> variant
pair and produce individual OpenType substitution statements in font order.
Why: A feature draft is easier to review when its name relationships are visible.
Usage: Enter a suffix without the dot, Refresh, then Copy Result. Paste the
statements into a chosen feature in FontLab and compile there after review.
Benefit: Inspect proposed substitutions before use.
The graph infers names only; it does not read, validate or compile feature code.
The full text draft is retained; the scene shows at most 100 pairs.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt diagramscene example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Source: rescued/part2/ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py
SHA256: 9a955af5875f27bba1baad27d5c508910c80a5ec6463d7cb00890e983322fe56
Source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py
SHA256: 2f1d99279f78a43459928e59388681eb4ded7a85f0bd7b3cb6a7593980d05f1e

Run **Graphics > Glyph Variant Feature Graph** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4d74f523a0ecadfafb5ca056bf8bd66a8457d2d151a86fc59dd8ac1b7dae305c.py)
<!--/codeinclude-->
