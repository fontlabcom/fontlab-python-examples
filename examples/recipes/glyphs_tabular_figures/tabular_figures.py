#MenuTitle: Tabular Figures
# this_file: examples/recipes/glyphs_tabular_figures/tabular_figures.py
__doc__ = """
Centre the selected glyphs' outlines in one fixed advance width (Glyphs 3 or 4).

Written against the Glyphs 3 API. Verified in FontLab through glyport (see recipe.py);
not yet run in Glyphs itself.
"""

WIDTH = 600


def outline_extent(layer):
    """(left, right) of the layer's nodes, or None for an empty layer."""
    xs = [node.x for path in layer.paths for node in path.nodes]
    return (min(xs), max(xs)) if xs else None


def centre_shift(left, right, width):
    """Whole-unit horizontal shift that centres left..right in width."""
    return round((width - (right - left)) / 2 - left)


def centre_in_width(layer, width=WIDTH):
    """Move the outline (and anchors) to the centre of ``width``; returns the shift."""
    extent = outline_extent(layer)
    if extent is None:
        return None
    shift = centre_shift(extent[0], extent[1], width)
    for path in layer.paths:
        for node in path.nodes:
            node.x = node.x + shift
    if layer.anchors:
        from Foundation import NSPoint  # Glyphs; glyport cannot move anchors yet

        for anchor in layer.anchors:
            anchor.position = NSPoint(anchor.position.x + shift, anchor.position.y)
    layer.width = width
    return shift


def tabular_figures(font, glyph_names, width=WIDTH, master_index=0):
    """Centre ``glyph_names`` in ``width`` on one master; returns {name: shift}."""
    master = font.masters[master_index]
    shifts = {}
    for name in glyph_names:
        glyph = font.glyphs[name]
        if glyph is None:
            print(f"{name}: not in the font")
            continue
        shifts[name] = centre_in_width(glyph.layers[master.id], width)
        print(f"{name}: shifted {shifts[name]}, width {width}")
    return shifts


if __name__ == "__main__":
    from GlyphsApp import Glyphs

    font = Glyphs.font
    tabular_figures(font, [layer.parent.name for layer in font.selectedLayers])
