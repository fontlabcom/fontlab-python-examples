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

Run **Drag And Drop > Draggable Glyph Names** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/366fe2e09e40a33a446e3dfdddc665f8e5d7db7b7538b25bf1ae08da88d92142.py)
<!--/codeinclude-->
