---
this_file: src_docs/md/current/tools/symbol-tag-search.md
tags: ["Tools"]
categories: ["Tools"]
---

# Symbol Tag Search

What: Find symbols by native glyph name and tags in the current font.
How: Match all space-separated terms, without case, against each name and tag.
Read names and tags once per refresh; report skipped names. Copy slash names to a Glyph window.
Why: Native tags travel with the font and need no external symbol database.
Usage: Enter name or tag terms. Refresh Result shows matches in font order.
Copy Fresh Result reads the current font again before it copies the proof.
Benefit: Prepare a proof of related symbols, including unencoded glyphs.
This tool reads native tags. External textproto categories, visual similarity,
contour-part assembly and transforms are outside this search tool's scope.
Use FontLab's contour selection and Edit > Copy / Paste for contour parts.
The Font window sidebar > Tags filter searches native tags. This tool matches
several terms across names and tags together and copies an ordered slash proof.

Independent behaviour-only rewrite of the symbol-search idea from Explorer.py.
Credit: Vassil Kateliev and Karandash Type Foundry; kateliev/TypeRig, MPL-2.0.
No TypeRig code, comments, icons or resources are included.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Run **Tools > Symbol Tag Search** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `d79ca108fadfae9649ed60765d745722d956a930a6a3d3d22bd27a9bbe04cdd9`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Tools/Symbol%20Tag%20Search.py)
