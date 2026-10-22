---
this_file: src_docs/md/current/tools/copy-layers-from-font.md
tags: ["Tools"]
categories: ["Tools"]
---

# Copy Layers From Font

What: Copy layers from another open font to selected current-font glyphs.
How: Map source and destination layer names. Preview and confirm Overwrite,
Incoming + suffix, Destination + suffix or Mask. One Copy is recorded as one
Undo step in the destination. Both fonts are identified by fgId.
Why: Native Paste Special uses the clipboard; this repeats explicit layer maps
without switching fonts. The source is read only and glyphs must already exist.
Usage: Select destination glyphs in its Font window, choose a source, enter
mappings, Preview, inspect kept rows, confirm, then Copy.
Benefit: Transfer outlines, anchor positions and advances across many glyphs.

Components, hints, guides, metric expressions, locked/automatic layers and
unsafe automatic dependants are kept. Element names, notes and transforms,
contour names, node names and raw flags are retained; selection flags clear.
Custom node/contour properties are refused. Anchor coordinates use App;
existing
pin styles stay, new pins use name-derived styles. Anchor expressions, layer
metadata, links and colour marks are not copied. Units per em must match.
Mask replaces the mapped layer's mask. Destination + suffix refuses master
renames; existing suffix names are kept. New names cannot contain @ or # or
begin with |temp|, mask, img. or bw.. Capture allows 3 seconds plus
one second per selected glyph/mapping; a timeout refuses the whole preview.
Apply rechecks the displayed plan. Partial failures direct
you to Edit > Undo. Setup: FontLab 9, Python 3.11, Fly, App>=0.2.150.dev0.
Independent behaviour rewrite of TR-CopyLayers.py, Vassil Kateliev / Karandash
Type Foundry, kateliev/TypeRig, MPL-2.0. https://github.com/kateliev/TypeRig
No upstream code, comments or assets copied. Implementation: Apache-2.0.

Run **Tools > Copy Layers From Font** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a82d9f63fd25a2f33b4cc64cba7ce23a1df70202ca3fef4a29b10f64aa714ebd.py)
<!--/codeinclude-->
