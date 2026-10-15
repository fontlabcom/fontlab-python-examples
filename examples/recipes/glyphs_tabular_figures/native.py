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


BOLD = r"""
import fontlab
package = fontlab.flWorkspace.instance().findPackageId(font_id)
package.addMaster("Bold", True, package, "Regular", True, True)
package.setMaster("Bold", True)
result = [list(package.masters), package.master]
"""


def setup(fl, font_id):
    """A second master, current: the script must change Bold only."""
    made = fl.run(BOLD, font_id=font_id).value
    assert made == [["Regular", "Bold"], "Bold"], made


def check(report, glyphs, fl, font_id):
    one, two, a = (read_layer(glyphs[k], "Bold") for k in ("one", "two", "A"))
    regular = read_layer(glyphs["one"], "Regular")
    return {
        "regular_master_untouched": regular["width"] == 350.0
        and regular["contours"][0][0] == (100.0, 0.0),
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
        setup=setup,
    )
