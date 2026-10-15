#MenuTitle: Copy Sidebearings from Reference Glyph
# this_file: examples/recipes/sidebearings_from_reference/recipe.py
"""Give glyphs the left and right sidebearings of a reference glyph.

For each target, the outline and anchors shift horizontally so that its left
sidebearing equals the reference's, and the advance width is set so that the
right sidebearing matches too: "H" spacing for "I", "n" for "h m". Glyphs
without outlines are skipped. Run layer_backup first: Edit > Undo does not
restore script edits in FontLab 9.0.9783.
"""


def sidebearings(left: float, right: float, width: float) -> tuple[float, float]:
    """(LSB, RSB) of an outline spanning left..right in an advance of width."""
    return left, width - right


def respace(left: float, right: float, lsb: float, rsb: float) -> tuple[float, float]:
    """(horizontal shift, new advance width) giving the outline these sidebearings."""
    return lsb - left, lsb + (right - left) + rsb


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


def _extent(layer):
    box = layer.boundingBox
    return box.x(), box.x() + box.width()


def run(font_id=None, glyph_names=None, reference="H", master=None) -> dict:
    """Respace targets (default: all except the reference); returns {glyph: [lsb, rsb]}."""
    import fontlab
    from PythonQt.QtCore import QPointF

    package, glyphs = _targets(font_id, glyph_names)
    master = master or package.master
    source = package.findName(reference)
    source_layer = source.findLayer(master) if source is not None else None
    if source_layer is None or not source_layer.getContours():
        raise ValueError(f"Reference glyph {reference!r} has no outline on {master}")
    lsb, rsb = sidebearings(*_extent(source_layer), source_layer.advanceWidth)
    done, layers, changed = {}, [], []
    for glyph in glyphs:
        layer = glyph.findLayer(master)
        if glyph.name == reference or layer is None or not layer.getContours():
            continue
        shift, width = respace(*_extent(layer), lsb, rsb)
        for contour in layer.getContours():
            for node in contour.nodes():
                node.x = node.x + shift
        for anchor in layer.anchors:
            anchor.point = QPointF(anchor.point.x() + shift, anchor.point.y())
        layer.advanceWidth = width
        done[glyph.name] = [lsb, rsb]
        layers.append(layer)
        changed.append(glyph)
    if changed:
        fontlab.flItems().notifyChangesApplied("Copy sidebearings", layers + changed)
    return {"master": master, "reference": reference, "sidebearings": done}


# Menu use: fill these in, then run the script. Nothing happens while GLYPHS is empty.
REFERENCE = "H"
GLYPHS = []  # e.g. ["I", "J"]

if __name__ == "__main__":
    if GLYPHS:
        print(run(glyph_names=GLYPHS, reference=REFERENCE))
    else:
        print("Copy Sidebearings: set GLYPHS (and REFERENCE) at the end of this script first.")
