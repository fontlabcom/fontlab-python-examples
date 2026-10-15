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
    glyph("U", [], width=1000, unicode="0055"),  # curved contours added by setup()
]
# "U": a cubic hump drawn clockwise (curve peaks at y=750, handles at y=1000) and a
# clockwise square at y 800..900: inside the handles but outside the curve, so it
# is an outer contour and must end counter-clockwise.
ISLAND = [(450, 800), (450, 900), (550, 900), (550, 800)]
CURVED = r"""
import fontlab
from PythonQt.QtCore import QPointF
package = fontlab.flWorkspace.instance().findPackageId(font_id)
glyph = package.findName("U")
layer = glyph.findLayerCreate("Regular")
def contour(spec):
    nodes = [fontlab.flNode(QPointF(x, y), nodeType="on" if on else "off") for x, y, on in spec]
    return fontlab.flContour(nodes, closed=True)
shape = fontlab.flShape()
shape.addContour(contour([(0, 0, True), (0, 1000, False), (1000, 1000, False), (1000, 0, True)]), True)
shape.addContour(contour([(x, y, True) for x, y in island]), True)
layer.addShape(shape)
fontlab.flItems().notifyChangesApplied("fixture", [layer, glyph])
result = [len(c.nodes()) for c in layer.getContours()]
"""


def setup(fl, font_id):
    made = fl.run(CURVED, font_id=font_id, island=ISLAND).value
    assert made == [4, 4], made


def check(report, glyphs, fl, font_id):
    o = read_layer(glyphs["O"])["contours"]
    d = read_layer(glyphs["D"])["contours"]
    u = read_layer(glyphs["U"])["contours"]
    return {
        "curved_outer_counter_clockwise": signed_area(u[0]) > 0,
        "island_inside_handles_is_outer": signed_area(u[1]) > 0
        and sorted(u[1]) == sorted((float(x), float(y)) for x, y in ISLAND),
        "outer_counter_clockwise": signed_area(o[0]) > 0,
        "counter_clockwise_inner": signed_area(o[1]) < 0,
        "outer_starts_bottom_left": o[0][0] == (0.0, 0.0),
        "inner_starts_bottom_left": o[1][0] == (100.0, 100.0),
        "same_points": sorted(o[0]) == sorted((float(x), float(y)) for x, y in OUTER)
        and sorted(o[1]) == sorted((float(x), float(y)) for x, y in INNER),
        "correct_glyph_untouched": d == [[(float(x), float(y)) for x, y in GOOD]],
        "report": report["reversed"] == 4 and report["glyphs"] == ["O", "U"],
    }


if __name__ == "__main__":
    main("contour_direction", GLYPHS, {}, check, setup=setup)
