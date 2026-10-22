---
this_file: src_docs/md/current/tools/apply-unicode-map.md
tags: ["Tools"]
categories: ["Tools"]
---

# Apply Unicode Map

What: Add explicit Unicode values to selected glyphs in the current font.
How: Paste a JSON object of glyph names and code points. Integers are decimal;
strings are hexadecimal, with optional U+ or 0x prefix. A value can be a list. Existing codes stay in place.
Why: Font > Generate Unicodes derives values from names. This map also encodes
custom names and assigns several explicit values to one glyph.
Usage: Select glyphs in the Font window and close Glyph editors. Paste a map,
inspect the live table, then Apply Map. Use Selection reloads the glyph scope.
Each Apply is recorded as one Undo step. Auto-layer owners, bases of automatic
composites, unknown names and conflicting codes remain as named kept rows.
Benefit: Apply a reusable character map without renaming outlines.

Example: {"A": "0041", "space": [32, "00A0"]}. Repeated JSON keys and invalid
Unicode scalars are refused. Several map rows cannot claim the same code.
Only selected glyphs can change. Typing uses a detached font snapshot. Use Selection
reloads it. Apply scans the font once and compares with the displayed preview;
native read-back checks every changed list. A partial write directs you to
Edit > Undo. JSON is pasted; NAM files and font-library maps are not loaded.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0. Modeless panel.

Independent behaviour rewrite of TR-EncodeGlyphs.py by Vassil Kateliev,
kateliev/TypeRig, MPL-2.0. https://github.com/kateliev/TypeRig
No TypeRig code, private identifiers, comments or resources are copied.

Run **Tools > Apply Unicode Map** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/80440ee7ce34cba027f6284ea7a834438368b57d985c5f0a5f030024c21dd195.py)
<!--/codeinclude-->
