---
this_file: src_docs/md/current/widgets/glyph-character-map.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Glyph Character Map

Choose reference-font characters and check the current FontLab font's coverage.

Purpose:
    Compose a Unicode proof while seeing covered and missing FontLab characters.
Setup:
    FontLab 9, Python3.11, Fly and reviewed App>=0.2.103.dev0. Open a font
    for coverage. The grid renders an installed Reference Font, not unsaved
    FontLab outlines. Installs nothing and changes no font.
Run:
    Choose reference family, style, size and font merging; point at or select
    BMP cells, edit the proof text, and use the explicit clipboard button.
    Refresh FontLab coverage rereads every glyph and Unicode assignment while
    preserving proof text and reference-font choices. Close/Escape releases it.
Result:
    Filled cell corners mean covered; hollow corners mean missing. Tooltips
    name matching glyphs. The proof lists every occurrence, including repeats
    and non-BMP text, with all matching glyph names or MISSING. No coverage
    filter replaces the original selection rules. Empty fonts remain explicit.
Compatibility:
    Complete distinct character-map part2 profile: part2 fixed styles and
    size spin box append on any valid mouse click; part3 database styles/sizes,
    activated font/style changes and native cursor/selection insertion.
    Part3 isolated surrogate insertion is explicitly refused. Incomplete text
    cannot be copied; no replacement characters or silent sequence rewriting.
    Native PythonQt and complete font-preservation acceptance remain pending.
    Source: rescued/part2/ports/widgets/pyqt-official/charactermap-499e965d86347920.py

Run **Widgets > Glyph Character Map** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1380dcdcc67ca1c35848c8200aeb37af6ebc12b3d0a04460a57300567ce1dbb2.py)
<!--/codeinclude-->
