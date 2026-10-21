---
this_file: src_docs/md/current/text/calendar-proof-builder.md
tags: ["Text"]
categories: ["Text"]
---

# Calendar Proof Builder

What: Create a monthly numeral proof for the current font.

How: Read Unicode assignments. Build a Monday-first calendar and report missing
ASCII digits and the space separator. The HTML preview uses a reference font.

Why: Glyph names do not identify Unicode coverage reliably.

Usage: Set year and month. Select Build, then Copy. Paste into FontLab Metrics
to proof the actual font. Export New saves a complete UTF-8 HTML document.

Benefit: Check date spacing with realistic numeral sequences.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.

Run **Text > Calendar Proof Builder** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/b726e73756b3a77e8333ea2cddaf547bf4b24353d45d1068244fb68e42cea3db.py)
<!--/codeinclude-->
