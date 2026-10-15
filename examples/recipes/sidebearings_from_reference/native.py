# this_file: examples/recipes/sidebearings_from_reference/native.py
"""Native check: targets get the reference's LSB/RSB; anchors move with the outline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _native import glyph, main, read_layer

GLYPHS = [
    glyph("H", [[(60, 0), (60, 700), (540, 700), (540, 0)]], width=600, unicode="0048"),
    glyph(
        "I",
        [[(200, 0), (200, 700), (300, 700), (300, 0)]],
        width=700,
        unicode="0049",
        anchors={"top": (250, 700)},
    ),
    glyph("space", [], width=250, unicode="0020"),
]


def check(report, glyphs, fl, font_id):
    h, i, space = (read_layer(glyphs[k]) for k in ("H", "I", "space"))
    return {
        "i_outline_shifted": i["contours"]
        == [[(60.0, 0.0), (60.0, 700.0), (160.0, 700.0), (160.0, 0.0)]],
        "i_width": i["width"] == 220.0,
        "i_anchor_shifted": i["anchors"] == {"top": (110.0, 700.0)},
        "reference_untouched": h["width"] == 600.0
        and h["contours"][0][0] == (60.0, 0.0),
        "empty_skipped": space["width"] == 250.0,
        "report": report["sidebearings"] == {"I": [60.0, 60.0]},
    }


if __name__ == "__main__":
    main("sidebearings_from_reference", GLYPHS, {"reference": "H"}, check)
