# this_file: examples/recipes/contour_direction/native.py
"""Native check: outer contour counter-clockwise, counter clockwise, bottom-left starts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _native import glyph, main, read_layer, signed_area

# "O": outer square drawn clockwise and starting top-right; counter drawn
# counter-clockwise starting top-left. Both wrong for PostScript direction.
OUTER = [(500, 700), (500, 0), (0, 0), (0, 700)]
INNER = [(100, 600), (100, 100), (400, 100), (400, 600)]
GOOD = [(0, 0), (600, 0), (600, 700), (0, 700)]
GLYPHS = [
    glyph("O", [OUTER, INNER], width=500, unicode="004F"),
    glyph("D", [GOOD], width=600, unicode="0044"),
]


def check(report, glyphs, fl, font_id):
    o = read_layer(glyphs["O"])["contours"]
    d = read_layer(glyphs["D"])["contours"]
    return {
        "outer_counter_clockwise": signed_area(o[0]) > 0,
        "counter_clockwise_inner": signed_area(o[1]) < 0,
        "outer_starts_bottom_left": o[0][0] == (0.0, 0.0),
        "inner_starts_bottom_left": o[1][0] == (100.0, 100.0),
        "same_points": sorted(o[0]) == sorted((float(x), float(y)) for x, y in OUTER)
        and sorted(o[1]) == sorted((float(x), float(y)) for x, y in INNER),
        "correct_glyph_untouched": d == [[(float(x), float(y)) for x, y in GOOD]],
        "report": report["reversed"] == 2 and report["glyphs"] == ["O"],
    }


if __name__ == "__main__":
    main("contour_direction", GLYPHS, {}, check)
