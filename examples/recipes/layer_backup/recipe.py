#MenuTitle: Back Up Master Layers
# this_file: examples/recipes/layer_backup/recipe.py
"""Copy each glyph's master layer to a "<master> backup" layer before risky edits.

Run from FontLab's Scripting panel or Scripts menu: every glyph of the current
font (or ``glyph_names``) gets a non-master copy of its current master layer,
named "Regular backup", "Regular backup 2"... The master layer stays active.
Use it before other recipes: Edit > Undo does not restore script edits in
FontLab 9.0.9783.
"""

SUFFIX = " backup"


def backup_name(master: str, existing: list[str], suffix: str = SUFFIX) -> str:
    """First free "<master><suffix>" or "<master><suffix> N" layer name."""
    name, n = master + suffix, 2
    while name in existing:
        name, n = f"{master}{suffix} {n}", n + 1
    return name


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


def run(font_id=None, glyph_names=None, master=None, suffix=SUFFIX) -> dict:
    """Back up ``master`` (default: the font's current master); returns {glyph: layer}."""
    import fontlab

    package, glyphs = _targets(font_id, glyph_names)
    master = master or package.master
    made, layers, changed = {}, [], []
    for glyph in glyphs:
        layer = glyph.findLayer(master)
        if layer is None:  # glyph has no outline layer for this master yet
            continue
        copy = layer.clone()
        copy.name = backup_name(master, [item.name for item in glyph.layers], suffix)
        glyph.addLayer(copy)
        layer.setActive()  # addLayer activates the copy; keep editing the master
        made[glyph.name] = copy.name
        layers.append(copy)
        changed.append(glyph)
    if changed:
        # Changed layers, then their glyphs, in one list (refreshes FontLab's views).
        fontlab.flItems().notifyChangesApplied("Back up master layers", layers + changed)
    return {"master": master, "backups": made}


if __name__ == "__main__":
    print(run())
