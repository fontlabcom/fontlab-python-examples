# this_file: Scripts/Widgets/Glyph Character Map.py
# SPDX-License-Identifier: Apache-2.0
"""Choose reference-font characters and check the current FontLab font's coverage.

Purpose:
    Compose a Unicode proof while seeing covered and missing FontLab characters.
Setup:
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
    Complete distinct character-map part2 profile: part2 fixed styles and
    size spin box append on any valid mouse click; part3 database styles/sizes,
    activated font/style changes and native cursor/selection insertion.
    Part3 isolated surrogate insertion is explicitly refused. Incomplete text
    cannot be copied; no replacement characters or silent sequence rewriting.
    Historical source: rescued/part2/ports/widgets/pyqt-official/charactermap-499e965d86347920.py
"""
# historical source sha256: 3320979640264c11b88456cdadb40d8276086cf61f324315c3583c5ce9f2b285


def main() -> None:
    """Open the complete reference picker through Fly's lazy App namespace."""
    from fly.ap.character_map import show

    show()


if __name__ == "__main__":
    main()
