#MenuTitle: Correct Contour Direction and Start Points
# this_file: examples/recipes/contour_direction/recipe.py
"""PostScript contour direction and bottom-left start points for the current master.

Outer contours run counter-clockwise and counters clockwise (the PostScript/CFF
convention, in FontLab's y-up coordinates); nesting decides which is which.
Each contour then starts at its lowest, then leftmost on-curve node. The
orientation is computed here from the nodes rather than read from FontLab.
"""


def signed_area(points: list[tuple[float, float]]) -> float:
    """Shoelace area in y-up coordinates: positive means counter-clockwise."""
    pairs = zip(points, points[1:] + points[:1])
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in pairs) / 2


def contains(polygon: list[tuple[float, float]], point: tuple[float, float]) -> bool:
    """Even-odd ray test: is ``point`` inside ``polygon``?"""
    x, y = point
    inside = False
    for (x0, y0), (x1, y1) in zip(polygon, polygon[1:] + polygon[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def wants_counter_clockwise(contours: list[list[tuple[float, float]]], index: int) -> bool:
    """Outer (even nesting depth) contours run counter-clockwise."""
    probe = contours[index][0]
    depth = sum(contains(other, probe) for i, other in enumerate(contours) if i != index)
    return depth % 2 == 0


def start_index(points: list[tuple[float, float]], on_curve: list[bool]) -> int:
    """Index of the lowest, then leftmost, on-curve point."""
    candidates = [i for i, on in enumerate(on_curve) if on] or list(range(len(points)))
    return min(candidates, key=lambda i: (points[i][1], points[i][0]))


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


def run(font_id=None, glyph_names=None, master=None) -> dict:
    """Fix direction and start point of every closed contour; returns what changed."""
    import fontlab

    package, glyphs = _targets(font_id, glyph_names)
    master = master or package.master
    reversed_, restarted, layers, changed = 0, 0, [], []
    for glyph in glyphs:
        layer = glyph.findLayer(master)
        if layer is None:
            continue
        contours = [c for c in layer.getContours() if c.closed]
        shapes = [[(n.x, n.y) for n in c.nodes()] for c in contours]
        touched = False
        for index, contour in enumerate(contours):
            ccw = signed_area(shapes[index]) > 0
            if ccw != wants_counter_clockwise(shapes, index):
                contour.reverse()
                reversed_ += 1
                touched = True
            nodes = contour.nodes()
            first = start_index([(n.x, n.y) for n in nodes], [n.isOn() for n in nodes])
            if first:
                contour.setStartPoint(first)
                restarted += 1
                touched = True
        if touched:
            layers.append(layer)
            changed.append(glyph)
    if changed:
        fontlab.flItems().notifyChangesApplied("Correct contour direction", layers + changed)
    return {"master": master, "reversed": reversed_, "restarted": restarted,
            "glyphs": [g.name for g in changed]}


if __name__ == "__main__":
    print(run())
