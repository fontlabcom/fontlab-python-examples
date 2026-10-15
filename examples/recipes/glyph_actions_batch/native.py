# this_file: examples/recipes/glyph_actions_batch/native.py
"""Native check: Remove Overlap through fontlabapp merges two squares into one contour."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _native import glyph, main, read_layer

GLYPHS = [
    glyph(
        "X",
        [
            [(0, 0), (0, 400), (400, 400), (400, 0)],
            [(200, 200), (200, 600), (600, 600), (600, 200)],
        ],
        width=600,
        unicode="0058",
    ),
    glyph(
        "Y",
        [
            [(0, 0), (0, 400), (400, 400), (400, 0)],
            [(200, 200), (200, 600), (600, 600), (600, 200)],
        ],
        width=600,
        unicode="0059",
    ),
]


def check(report, glyphs, fl, font_id):
    x, y = read_layer(glyphs["X"]), read_layer(glyphs["Y"])
    points = [p for contour in x["contours"] for p in contour]
    return {
        "x_merged_to_one_contour": len(x["contours"]) == 1,
        "x_union_bounds": (
            min(p[0] for p in points),
            min(p[1] for p in points),
            max(p[0] for p in points),
            max(p[1] for p in points),
        )
        == (0.0, 0.0, 600.0, 600.0),
        "x_union_points": len(points) == 8,
        "y_not_named_untouched": len(y["contours"]) == 2,
        "related_menu_found": any(
            "Overlap" in path for path in report["related_menu_commands"]
        ),
    }


if __name__ == "__main__":
    main(
        "glyph_actions_batch",
        GLYPHS,
        {"glyph_names": ["X"]},
        check,
        needs=("fontlabapp",),
    )
