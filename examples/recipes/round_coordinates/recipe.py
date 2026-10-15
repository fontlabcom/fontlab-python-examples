#MenuTitle: Round Coordinates to Grid
# this_file: examples/recipes/round_coordinates/recipe.py
"""Snap node, anchor and advance-width values of the current master to a grid.

Fractional coordinates appear after scaling, interpolation or imports. This
rounds every node (on- and off-curve), anchor and advance width of the current
master to multiples of ``grid`` (1 = whole units), half away from zero, as one
Edit > Undo step. Coordinates are in each shape's own space.
"""

import math


def snap(value: float, grid: float = 1) -> float:
    """Nearest multiple of ``grid``; halves round away from zero (-2.5 -> -3)."""
    if grid <= 0:
        raise ValueError("grid must be positive")
    steps = math.floor(abs(value) / grid + 0.5)
    return math.copysign(steps * grid, value) if steps else 0.0


def _targets(font_id, glyph_names):
    """The package and its flGlyphs: named ones, or all except .notdef."""
    import fontlab
    import fontpr

    if font_id is None:  # FontLab's font id (flPackage.id is not it)
        font_id = fontpr.call("get_active_font")["id"]
    package = fontlab.flWorkspace.instance().findPackageId(font_id)
    if package is None:
        raise RuntimeError(f"No open font with id {font_id}")
    if glyph_names is None:
        listed = fontpr.call("list_glyphs", font_id=font_id, limit=100000)["glyphs"]
        glyph_names = [g["name"] for g in listed if g["name"] != ".notdef"]
    glyphs = [package.findName(name) for name in glyph_names]
    missing = [n for n, g in zip(glyph_names, glyphs) if g is None]
    if missing:
        raise KeyError(f"Glyphs not in the font: {missing}")
    return package, glyphs


def run(font_id=None, glyph_names=None, grid=1, anchors=True, width=True, master=None) -> dict:
    """Round the master layer of each glyph; returns counts of changed values."""
    import fontlab
    from PythonQt.QtCore import QPointF

    package, glyphs = _targets(font_id, glyph_names)
    master = master or package.master
    counts = {"nodes": 0, "anchors": 0, "widths": 0}
    layers, changed = [], []
    for glyph in glyphs:
        layer = glyph.findLayer(master)
        if layer is None:
            continue
        before = dict(counts)
        for contour in layer.getContours():
            for node in contour.nodes():
                x, y = snap(node.x, grid), snap(node.y, grid)
                if (x, y) != (node.x, node.y):
                    node.x, node.y = x, y
                    counts["nodes"] += 1
        for anchor in layer.anchors if anchors else ():
            point = anchor.point
            x, y = snap(point.x(), grid), snap(point.y(), grid)
            if (x, y) != (point.x(), point.y()):
                anchor.point = QPointF(x, y)
                counts["anchors"] += 1
        if width and snap(layer.advanceWidth, grid) != layer.advanceWidth:
            layer.advanceWidth = snap(layer.advanceWidth, grid)
            counts["widths"] += 1
        if counts != before:
            layers.append(layer)
            changed.append(glyph)
    if changed:
        fontlab.flItems().notifyChangesApplied("Round coordinates", layers + changed)
    return {"master": master, "grid": grid, "changed": counts, "glyphs": [g.name for g in changed]}


if __name__ == "__main__":
    print(run())
