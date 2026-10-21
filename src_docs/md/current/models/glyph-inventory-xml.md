---
this_file: src_docs/md/current/models/glyph-inventory-xml.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Inventory XML

What: Export the current font's glyph names, Unicode values and revision dates.
How: Read the App glyph catalogue and build XML elements with the standard
library. Escape names and refuse characters that XML cannot represent.
Why: Explicit elements retain every Unicode assignment for later scripts.
Usage: Open a font and Refresh. Inspect the rows, then Copy Report or Export New.
Benefit: Feed a small glyph inventory to a scripting or comparison pipeline.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Export requires a new absolute path and never overwrites a file.

Independent rewrite of the Qt simpledommodel example idea. Based on the author's own FontLab sample,
Apache-2.0.
Source: rescued/part2/ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py
SHA256: c17809b93a3fff1601c20e15f233edbf687f023430e86bf1986772e38bf712d6
Source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py
SHA256: 50abde2890c2ca53384733ee94f77b54e3b4b7783efba2a965fc8b68a9becb42

Run **Models > Glyph Inventory XML** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/31b8eec37467378a9e5f6886973c1b839ec50db4c954ff7e3f14f353e20f954f.py)
<!--/codeinclude-->
