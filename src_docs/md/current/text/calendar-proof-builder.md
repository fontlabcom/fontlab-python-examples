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

## Source identity

SHA256: `7e0ed7debff0aef538d9f1638628055ee5cdfa1ec9c50fbc1207cdc7f8f63bda`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Text/Calendar%20Proof%20Builder.py)
