---
this_file: src_docs/md/current/tools/import-kerning-pair-list.md
tags: ["Tools"]
categories: ["Tools"]
---

# Import Kerning Pair List

What: Import many current-master kerning pairs from a pasted text list.
How: Read left right value lines; # begins a comment. Preview every row before
Apply. Decimal values round half away from zero to whole units. Invalid rows
block the entire batch. Duplicate pair lines require correction.
Why: A pair list can carry different values for many glyph and class pairs.
Usage: Open a font, paste the list, press Preview and inspect the table. Press
Apply for one Undo step. Edit the list and Preview again for another batch.
Benefit: Transfer measured pairs without creating glyphs or kerning classes.

@class names must already exist on the correct side of the current master's
kerning. Glyphs with automatic layers, including members of a named class,
are refused by the shared FontLab editing rules. Apply checks the font,
master, text and complete kerning snapshot again. Native read-back verifies
the written batch. Keep the panel open for repeated imports.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Based on the author's own FontLab sample, Apache-2.0.
Source: recipe.py (Kerning Pairs from Text).

Run **Tools > Import Kerning Pair List** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/b392ca95cda592efde3680f4dd24c033db5c5457179aac51d18ff5c434084cdb.py)
<!--/codeinclude-->
