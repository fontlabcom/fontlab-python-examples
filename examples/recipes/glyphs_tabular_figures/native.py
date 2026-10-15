# this_file: examples/recipes/glyphs_tabular_figures/native.py
"""Native check: the unchanged Glyphs script centres figures in 600 units via glyport."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _native import glyph, main, read_layer

GLYPHS = [
    glyph(
        "one", [[(100, 0), (100, 700), (200, 700), (200, 0)]], width=350, unicode="0031"
    ),
    glyph(
        "two", [[(40, 0), (40, 700), (540, 700), (540, 0)]], width=580, unicode="0032"
    ),
    glyph("A", [[(50, 0), (300, 700), (550, 0)]], width=600, unicode="0041"),
]


def check(report, glyphs, fl, font_id):
    one, two, a = (read_layer(glyphs[k]) for k in ("one", "two", "A"))
    return {
        "one_centred": one["width"] == 600.0 and one["contours"][0][0] == (250.0, 0.0),
        "two_centred": two["width"] == 600.0 and two["contours"][0][0] == (50.0, 0.0),
        "letter_untouched": a["width"] == 600.0 and a["contours"][0][0] == (50.0, 0.0),
        "report": report["shifts"] == {"one": 150, "two": 10},
        "script_printed": "one: shifted 150, width 600" in report["output"],
    }


if __name__ == "__main__":
    main(
        "glyphs_tabular_figures",
        GLYPHS,
        {"width": 600},
        check,
        needs=("fontlab_glyport",),
    )
