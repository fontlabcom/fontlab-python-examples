# this_file: examples/recipes/layer_backup/native.py
"""Native check: backups are independent copies, the master stays active."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _native import glyph, main, read_layer

SQUARE = [(100, 0), (100, 500), (400, 500), (400, 0)]
GLYPHS = [
    glyph("O", [SQUARE], width=500, unicode="004F"),
    glyph("H", [[(50, 0), (50, 700), (150, 700), (150, 0)]], width=600, unicode="0048"),
]
EDIT = r"""
import fontlab
package = fontlab.flWorkspace.instance().findPackageId(font_id)
node = package.findName("O").findLayer("Regular").getContours()[0].nodes()[0]
node.x = 111
result = None
"""


def check(report, glyphs, fl, font_id):
    o = glyphs["O"]["layers"]
    names = [layer["name"] for layer in o]
    backup_before = read_layer(glyphs["O"], "Regular backup")
    # A second run must pick a fresh name; then edit the master and re-read.
    second = fl.run(
        "import importlib.util\nspec = importlib.util.spec_from_file_location('r', path)\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "result = m.run(font_id=font_id, glyph_names=['O'])",
        path=str(Path(__file__).with_name("recipe.py")),
        font_id=font_id,
    ).value
    fl.run(EDIT, font_id=font_id)
    after = fl.tool("get_glyph", font_id=font_id, glyph_name="O")
    return {
        "report_lists_both": report["backups"]
        == {"O": "Regular backup", "H": "Regular backup"},
        "backup_layer_added": names == ["Regular", "Regular backup"],
        "backup_has_master_outline": backup_before["contours"]
        == [[(float(x), float(y)) for x, y in SQUARE]],
        "master_still_active": not any(
            layer.get("active") for layer in o if layer["name"] != "Regular"
        ),
        "second_run_new_name": second["backups"] == {"O": "Regular backup 2"},
        "backup_independent_of_master": read_layer(after, "Regular backup")["contours"][
            0
        ][0]
        == (100.0, 0.0)
        and read_layer(after, "Regular")["contours"][0][0] == (111.0, 0.0),
    }


if __name__ == "__main__":
    main("layer_backup", GLYPHS, {}, check)
