---
this_file: src_docs/md/current/drag-and-drop/draggable-glyph-names.md
tags: ["Drag And Drop"]
categories: ["Drag And Drop"]
---

# Draggable Glyph Names

Drag exact current-font glyph names into a FontLab proof.

Open a font, run this panel and Refresh after changing fonts. Enter an optional
name filter and choose Use input. Select rows and drag the slash-name tokens
into a Glyph window text bar. Copy output copies all displayed tokens.
Names retain suffixes and unencoded glyphs, so proof assembly does not depend
on Unicode assignments. Filtering and copy-only dragging leave the font intact.
This panel sends text; it does not accept incoming drops.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Draggable Glyph Names profile.

Run **Drag And Drop > Draggable Glyph Names** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `95cb03a7a394bee9f9cf21a1d79cb7f89a8e242db90f60116c2f781509c49e8b`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Drag%20And%20Drop/Draggable%20Glyph%20Names.py)
