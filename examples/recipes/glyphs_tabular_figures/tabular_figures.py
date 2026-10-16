#MenuTitle: Tabular Figures
# this_file: examples/recipes/glyphs_tabular_figures/tabular_figures.py
__doc__ = """
Centre the selected glyphs' outlines in one fixed advance width (Glyphs 3 or 4).

Written against the Glyphs 3 API. Verified in FontLab through glyport (see recipe.py)
and inside Glyphs 3.5.1 and 4.2 on an in-memory test font.
"""

WIDTH = 600


def _cubic_xs(a, b, c, d):
    """x of the end points and of the curve's interior extrema (not its handles)."""
    xs = [a, d]
    qa, qb, qc = -a + 3 * b - 3 * c + d, 2 * (a - 2 * b + c), b - a  # derivative / 3
    if abs(qa) < 1e-12:
        roots = [-qc / qb] if abs(qb) > 1e-12 else []
    else:
        disc = qb * qb - 4 * qa * qc
        roots = [] if disc < 0 else [(-qb + s * disc ** 0.5) / (2 * qa) for s in (1, -1)]
    for t in roots:
        if 0 < t < 1:
            xs.append((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d)
    return xs


def _quad_xs(a, b, c):
    xs = [a, c]
    denominator = a - 2 * b + c
    if abs(denominator) > 1e-12 and 0 < (a - b) / denominator < 1:
        t = (a - b) / denominator
        xs.append((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * c)
    return xs


def outline_extent(layer):
    """(left, right) of the actual outline (curve extrema, not handles), or None."""
    xs = []
    for path in layer.paths:
        nodes = list(path.nodes)
        ons = [i for i, node in enumerate(nodes) if node.type != "offcurve"]
        if nodes and not ons:
            raise ValueError("paths made only of off-curve points are not supported")
        for k, i in enumerate(ons):
            end = nodes[i]
            if k == 0 and not path.closed:
                xs.append(end.x)
                continue
            start = ons[k - 1]
            between = [nodes[j % len(nodes)].x for j in range(start + 1, i + (len(nodes) if i <= start else 0))]
            a, d = nodes[start].x, end.x
            if not between:
                xs += [a, d]
            elif len(between) == 2 and end.type == "curve":
                xs += _cubic_xs(a, between[0], between[1], d)
            else:  # TrueType quadratic run with implied on-curve midpoints
                for n, handle in enumerate(between):
                    stop = d if n == len(between) - 1 else (handle + between[n + 1]) / 2
                    xs += _quad_xs(a, handle, stop)
                    a = stop
    return (min(xs), max(xs)) if xs else None


def centre_shift(left, right, width):
    """Whole-unit horizontal shift that centres left..right in width."""
    return round((width - (right - left)) / 2 - left)


def centre_in_width(layer, width=WIDTH):
    """Move the outline (and anchors) to the centre of ``width``; returns the shift.

    Layers with components are refused before any change: their bounds depend on
    other glyphs.
    """
    if getattr(layer, "components", None):
        raise ValueError("layer has components; decompose or centre the base glyphs first")
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


def tabular_figures(font, glyph_names, width=WIDTH, master_id=None):
    """Centre ``glyph_names`` in ``width`` on one master (default: the selected
    master); returns {name: shift}. An empty list does nothing."""
    if master_id is None:
        master_id = font.selectedFontMaster.id
    shifts = {}
    for name in glyph_names:
        glyph = font.glyphs[name]
        if glyph is None:
            print(f"{name}: not in the font")
            continue
        shifts[name] = centre_in_width(glyph.layers[master_id], width)
        print(f"{name}: shifted {shifts[name]}, width {width}")
    return shifts


if __name__ == "__main__":
    from GlyphsApp import Glyphs

    font = Glyphs.font
    tabular_figures(font, [layer.parent.name for layer in font.selectedLayers])
