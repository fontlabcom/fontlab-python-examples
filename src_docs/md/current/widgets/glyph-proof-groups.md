---
this_file: src_docs/md/current/widgets/glyph-proof-groups.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Glyph Proof Groups

What: Build a glyph-name proof from useful current-font groups.
How: Read a fresh App catalog. Combine encoded and unencoded glyphs in font
order, optionally omit suffix names, then wrap slash names into short lines.
Why: Explicit groups make a compact Metrics proof without changing selection.
Usage: Tick the desired groups and set names per line. Preview, then copy the
plain text into FontLab Metrics. Dots identify suffix names by convention.
Names outside portable slash syntax are omitted and listed in the status line.
Benefit: Compare base glyphs and alternates in repeatable proof groups.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Group Box example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.

Run **Widgets > Glyph Proof Groups** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a8d968aae673207eae15b25936de21e2a19dacfa817b2acd416c4d73060a8d0b.py)
<!--/codeinclude-->
