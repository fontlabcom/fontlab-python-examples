#MenuTitle: Place Top and Bottom Anchors
# this_file: examples/recipes/anchors_from_bounds/recipe.py
"""Add or move "top" and "bottom" anchors from each glyph's outline bounds.

"top" sits above the horizontal centre of the outline bounds, ``offset`` units
above the highest point; "bottom" sits on the baseline (y = 0) at the same x.
Existing anchors of those names are moved, others are left alone. Glyphs
without outlines are skipped.
"""


def anchor_positions(left: float, bottom: float, right: float, top: float,
                     offset: float = 0) -> dict[str, tuple[float, float]]:
    """{"top": (x, y), "bottom": (x, 0)} for outline bounds, rounded to units."""
    x = round((left + right) / 2)
    return {"top": (x, round(top + offset)), "bottom": (x, 0)}


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


def run(font_id=None, glyph_names=None, offset=0, master=None) -> dict:
    """Place both anchors on the master layer; returns {glyph: {anchor: [x, y]}}."""
    import fontlab
    from PythonQt.QtCore import QPointF

    package, glyphs = _targets(font_id, glyph_names)
    master = master or package.master
    placed, layers, changed = {}, [], []
    for glyph in glyphs:
        layer = glyph.findLayer(master)
        if layer is None or not layer.getContours():
            continue
        box = layer.boundingBox
        wanted = anchor_positions(box.x(), box.y(), box.x() + box.width(), box.y() + box.height(), offset)
        existing = {anchor.name: anchor for anchor in layer.anchors}
        for name, (x, y) in wanted.items():
            if name in existing:
                existing[name].point = QPointF(x, y)
            else:
                pin = fontlab.flPinPoint(QPointF(x, y))
                pin.name = name
                layer.addAnchor(pin)
        placed[glyph.name] = {name: list(xy) for name, xy in wanted.items()}
        layers.append(layer)
        changed.append(glyph)
    if changed:
        fontlab.flItems().notifyChangesApplied("Place anchors", layers + changed)
    return {"master": master, "anchors": placed}


if __name__ == "__main__":
    print(run())
