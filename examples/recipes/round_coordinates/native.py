# this_file: examples/recipes/round_coordinates/native.py
"""Native check: every node, anchor and width ends on the grid; one undo step."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _native import glyph, main, read_layer

GLYPHS = [
    glyph(
        "A",
        [[(10.4, 0.5), (300.6, 700.49), (589.5, -0.5)]],
        width=600.7,
        unicode="0041",
        anchors={"top": (300.5, 710.2)},
    ),
    glyph(
        "I", [[(100, 0), (100, 700), (200, 700), (200, 0)]], width=300, unicode="0049"
    ),
]
UNDO = r"""
import fontlab
from PythonQt import QtGui
action = [a for a in fontlab.flWorkspace.instance().mainWindow.children()
          if isinstance(a, QtGui.QAction) and a.objectName == "actionUndo"][0]
result = [action.enabled, action.text]
"""


def check(report, glyphs, fl, font_id):
    a, i = read_layer(glyphs["A"]), read_layer(glyphs["I"])
    undo = fl.run(UNDO).value
    return {
        "a_nodes_rounded": a["contours"]
        == [[(10.0, 1.0), (301.0, 700.0), (590.0, -1.0)]],
        "a_anchor_rounded": a["anchors"] == {"top": (301.0, 710.0)},
        "a_width_rounded": a["width"] == 601.0,
        "integer_glyph_untouched": report["glyphs"] == ["A"] and i["width"] == 300.0,
        "counts": report["changed"] == {"nodes": 3, "anchors": 1, "widths": 1},
        "one_undo_step": undo == [True, "&Undo Round Coordinates"],
    }


if __name__ == "__main__":
    main("round_coordinates", GLYPHS, {}, check)
