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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ad29c76dec5772082b81f596d7e4038e01744c08fa658d3af469a01981da8e14.py)
<!--/codeinclude-->
