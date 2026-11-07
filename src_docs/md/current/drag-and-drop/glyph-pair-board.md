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

Run **Drag And Drop > Glyph Pair Board** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `efd4c69ffa998a6138a5f73036eafa1ae3a5bf16ab21b6ac53a4f3e8dec50b8e`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Drag%20And%20Drop/Glyph%20Pair%20Board.py)
