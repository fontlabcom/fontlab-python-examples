# this_file: examples/recipes/anchors_from_bounds/native.py
"""Native check: anchors added or moved from bounds; other anchors and empty glyphs untouched."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _native import glyph, main, read_layer

GLYPHS = [
    glyph("A", [[(50, 0), (300, 700), (550, 0)]], width=600, unicode="0041"),
    glyph(
        "n",
        [[(60, 0), (60, 500), (440, 500), (440, 0)]],
        width=500,
        unicode="006E",
        anchors={"top": (10, 10), "ogonek": (400, 0)},
    ),
    glyph("space", [], width=250, unicode="0020"),
]


def check(report, glyphs, fl, font_id):
    a, n, space = (read_layer(glyphs[k]) for k in ("A", "n", "space"))
    return {
        "a_added": a["anchors"] == {"top": (300.0, 720.0), "bottom": (300.0, 0.0)},
        "n_top_moved_ogonek_kept": n["anchors"]
        == {"top": (250.0, 520.0), "ogonek": (400.0, 0.0), "bottom": (250.0, 0.0)},
        "empty_glyph_skipped": space["anchors"] == {}
        and "space" not in report["anchors"],
    }


if __name__ == "__main__":
    main("anchors_from_bounds", GLYPHS, {"offset": 20}, check)
