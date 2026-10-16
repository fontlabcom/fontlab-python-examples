# this_file: examples/recipes/glyphs_path_report/native.py
"""Native check: the unchanged Glyphs script reports exactly the planted problems; read-only."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _native import glyph, main, read_layer

GLYPHS = [
    glyph("O", [[(0, 0), (0, 700), (500, 700), (500, 0)]], width=500, unicode="004F"),
    glyph("dup", [[(0, 0), (0, 700), (0, 700), (500, 0)]], width=500),
    glyph(
        "tiny",
        [
            [(0, 0), (0, 300), (400, 300), (400, 0)],
            [(100, 100), (100, 102), (102, 102)],
        ],
        width=500,
    ),
    glyph("two", [[(0, 0), (500, 700)]], width=500),
]
EXPECTED = {
    "dup": ["path 1 repeats the point (0, 700)"],
    "tiny": ["path 2 is tiny (2 x 2)"],
    "two": ["path 1 has only 2 on-curve points"],
}


def check(report, glyphs, fl, font_id):
    o = read_layer(glyphs["O"])
    return {
        "exact_problems": report["problems"] == EXPECTED,
        "printed": "3 glyph(s) with path problems" in report["output"],
        "read_only": o["contours"]
        == [[(0.0, 0.0), (0.0, 700.0), (500.0, 700.0), (500.0, 0.0)]]
        and len(read_layer(glyphs["dup"])["contours"][0]) == 4,
    }


if __name__ == "__main__":
    main("glyphs_path_report", GLYPHS, {}, check, needs=("fontlab_glyport",))
