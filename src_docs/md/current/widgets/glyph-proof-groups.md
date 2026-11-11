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

Original profile setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Group Box example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Proof Composition Lab; opens the Glyph Proof Groups profile.

Run **Widgets > Glyph Proof Groups** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `ae2ed60f136b5f3411d894b27a7ac8a7c9b94786b5467c3318b8b4d619332dfc`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Widgets/Glyph%20Proof%20Groups.py)
