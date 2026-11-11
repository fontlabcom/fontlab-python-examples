---
this_file: src_docs/md/current/widgets/glyph-character-map-styles.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Glyph Character Map - Styles

Choose reference-font characters and check the current FontLab font's coverage.

Purpose:
    Compose a Unicode proof while seeing covered and missing FontLab characters.
Original profile setup:
    FontLab 9, Python3.11, Fly and App>=0.2.103.dev0. Open a font
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
    Complete distinct character-map part3 profile: part2 fixed styles and
    size spin box append on any valid mouse click; part3 database styles/sizes,
    activated font/style changes and native cursor/selection insertion.
    Part3 isolated surrogate insertion is explicitly refused. Incomplete text
    cannot be copied; no replacement characters or silent sequence rewriting.
    Historical source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/charactermap-499e965d86347920.py


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Unicode Lab; opens the Glyph Character Map - Styles profile.

Run **Widgets > Glyph Character Map - Styles** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `7411559a003c95b50817b3f3f90e931c80b602eb4ae6358a78fda0658593402c`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Widgets/Glyph%20Character%20Map%20-%20Styles.py)
