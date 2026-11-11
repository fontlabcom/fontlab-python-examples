---
this_file: src_docs/md/current/drag-and-drop/glyph-pair-board.md
tags: ["Drag And Drop"]
categories: ["Drag And Drop"]
---

# Glyph Pair Board

Build adjacent glyph-pair proof lines from the current font.

Open a font and enter or drop slash names, for example /A/V/A. Choose Use input
to append tiles. Drag rows to reorder them, or select rows and Remove selected.
Copy or drag output into a Glyph window text bar: each line contains one pair.
Names are checked before adding tiles. Repeated names, suffixes and unencoded
glyphs remain valid. Refresh clears the board for the newly captured font.
The board changes only the local proof order, never glyph order or kerning.
Prepare focused pair checks without entering each pair separately.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Glyph Pair Board profile.

Run **Drag And Drop > Glyph Pair Board** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `9b28a38edd5d9c7b51b2874904e9fe66dc2f2a910df45bc64baa64142d4487f9`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Drag%20And%20Drop/Glyph%20Pair%20Board.py)
