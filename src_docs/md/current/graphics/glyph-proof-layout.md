---
this_file: src_docs/md/current/graphics/glyph-proof-layout.md
tags: ["Graphics"]
categories: ["Graphics"]
---

# Glyph Proof Layout

What: Compare current-master advance widths and geometric side bearings.
How: Read a prefix-matched sample twice and build an anchored spacing strip.
Each tile's width is proportional to its advance. Hover for full measurements;
zero advances use a vertical marker and a separate measurement label.
Why: Compare relative widths at a glance while reviewing spacing in FontLab.
Usage: Open a font, enter a prefix with at most twelve matches, set the strip
width, then Refresh. Copy Result sends slash names to a Glyph window text bar.
Benefit: Spot width outliers without changing outlines or font metrics.
Empty layers have no ink margins; their side bearings show an em dash.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt anchorlayout example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Source: rescued/part2/ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py
SHA256: 4de40f5bc168015793f3529ef70f2e69dc46be41b38d17afb29f7e34ef8d717f
Source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py
SHA256: 60caa0dacfd8b8e41a4c8a5c83e5aced63a298e574433410c25e529452560ad2

Run **Graphics > Glyph Proof Layout** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/963d1905b0808d778e1dfe19d41ba1e3f17341d7a2ac77f138427031f6c04f1a.py)
<!--/codeinclude-->
