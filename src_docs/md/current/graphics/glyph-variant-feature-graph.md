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
Historical source: rescued/part2/ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py
SHA256: 9a955af5875f27bba1baad27d5c508910c80a5ec6463d7cb00890e983322fe56
Historical source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py
SHA256: 2f1d99279f78a43459928e59388681eb4ded7a85f0bd7b3cb6a7593980d05f1e

Run **Graphics > Glyph Variant Feature Graph** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `d9a142913ec14bea53254d7835bce4b474c01064a47ae74b1f3afc0650b01681`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Graphics/Glyph%20Variant%20Feature%20Graph.py)
