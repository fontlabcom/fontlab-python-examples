# this_file: examples/recipes/kerning_from_text/native.py
"""Native check: listed pairs land in FontLab's kerning with their values."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _native import glyph, main

SQUARE = [[(50, 0), (50, 500), (450, 500), (450, 0)]]
GLYPHS = [glyph(n, SQUARE, width=500, unicode=f"{ord(n):04X}") for n in "AVTo"]
TEXT = """# test pairs
A V -80
V A -75.5
T o -60
not a pair
"""


def pairs(fl, font_id):
    listed = fl.tool("list_kerning_pairs", font_id=font_id)
    return {(p["left"], p["right"]): p["value"] for p in listed["pairs"]}


def check(report, glyphs, fl, font_id):
    found = pairs(fl, font_id)
    return {
        "pairs_set": found == {("A", "V"): -80, ("V", "A"): -76, ("T", "o"): -60},
        "report_matches_stored": report["applied"]
        == [["A", "V", -80], ["V", "A", -76], ["T", "o", -60]],
        "bad_line_reported": report["unreadable"] == ["not a pair"],
        "report": len(report["applied"]) == 3,
    }


if __name__ == "__main__":
    main("kerning_from_text", GLYPHS, {"text": TEXT}, check)
