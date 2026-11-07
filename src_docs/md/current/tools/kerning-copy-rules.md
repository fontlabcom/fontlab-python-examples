---
this_file: src_docs/md/current/tools/kerning-copy-rules.md
tags: ["Tools"]
categories: ["Tools"]
---

# Kerning Copy Rules

What: Expand kerning copy rules into a current-master import list.
How: Read explicit pairs once. Use `A|V A|W = T|o @ -5` to copy T/o minus
five units to A/V and A/W. @class names use native kerning-class notation.
Every rule reads the original snapshot. No rule reads another rule's output.
Why: Reuse measured pairs without manual arithmetic or repeated pair edits.
Usage: Open a font. Enter rules. Build, inspect and Copy. Paste straight into
Tools > Import Kerning Pair List, then Preview and Apply. Export is optional.
Import uses the master that is current when you press Preview; check its status.
Benefit: Keep a reproducible pair list. This panel never changes the font.

Only explicit current-master pairs are read; inherited class results are not
guessed. All glyphs and class sides must exist. Offsets and results must be
whole units. A repeated destination or invalid row refuses the entire output.
The source supports all masters, automatic glyph-to-class lookup, character
tokens and arithmetic adjustments. This port keeps explicit current-master
glyph or @class tokens and integer additive adjustments only. It has no All
masters mode, automatic class lookup, character tokens, general arithmetic,
class-file import or direct application.
Use native Kerning panel > Copy Kerning From for complete-master transfers.
Requires FontLab 9, Python 3.11, Fly and App >= 0.2.150.dev0.

Credit: Independent behaviour rewrite of CopyKerning.py by Vassil Kateliev,
Karandash Type Foundry, kateliev/TypeRig, MPL-2.0.
https://github.com/kateliev/TypeRig
No source code, comments, icons or preset formats are copied.

Run **Tools > Kerning Copy Rules** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `e87db86b06d95a48cd72770e359095805e06fabb4985fc46c4c8bb38a2922f73`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Tools/Kerning%20Copy%20Rules.py)
