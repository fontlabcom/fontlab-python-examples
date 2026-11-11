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

Original profile setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Calendar Lab; opens the Calendar Proof Builder profile.

Run **Text > Calendar Proof Builder** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `13bdb19e3f0a47d339d70a76af2deed2b07f9ae9bb5a536fe98a5ba5b2bc2cfc`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Text/Calendar%20Proof%20Builder.py)
