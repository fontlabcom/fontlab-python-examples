#MenuTitle: Path Problem Report
# this_file: examples/recipes/glyphs_path_report/path_report.py
__doc__ = """
List open paths, paths with too few points, duplicate points and tiny paths (Glyphs 3 or 4).

Read-only. Written against the Glyphs 3 API. Verified in FontLab through glyport (see recipe.py)
and inside Glyphs 3.5.1 and 4.2 on an in-memory test font.
"""

MIN_SIZE = 4  # paths narrower or lower than this many units are reported as tiny


def _number(value):
    """Compact number text; -0.0 (which hosts do return) prints as 0."""
    return f"{value + 0.0:g}"


def path_problems(layer, min_size=MIN_SIZE):
    """Readable problem descriptions for one layer's paths."""
    problems = []
    for index, path in enumerate(layer.paths, 1):
        points = [(node.x, node.y) for node in path.nodes]
        on_curve = [node for node in path.nodes if node.type != "offcurve"]
        if not path.closed:
            problems.append(f"path {index} is open")
        elif len(on_curve) < 3:
            problems.append(f"path {index} has only {len(on_curve)} on-curve points")
        pairs = zip(points, points[1:] + (points[:1] if path.closed else []))
        for a, b in pairs:
            if a == b:
                problems.append(f"path {index} repeats the point ({_number(a[0])}, {_number(a[1])})")
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        if points and (max(xs) - min(xs) < min_size or max(ys) - min(ys) < min_size):
            problems.append(f"path {index} is tiny ({_number(max(xs) - min(xs))} x {_number(max(ys) - min(ys))})")
    return problems


def path_report(font, glyph_names=None, master_id=None):
    """{glyph name: [problems]} on one master (default: the selected master);
    prints one line per problem."""
    if master_id is None:
        master_id = font.selectedFontMaster.id
    report = {}
    for glyph in font.glyphs:
        if glyph_names is not None and glyph.name not in glyph_names:
            continue
        problems = path_problems(glyph.layers[master_id])
        if problems:
            report[glyph.name] = problems
            for problem in problems:
                print(f"{glyph.name}: {problem}")
    print(f"{len(report)} glyph(s) with path problems")
    return report


if __name__ == "__main__":
    from GlyphsApp import Glyphs

    font = Glyphs.font
    path_report(font, [layer.parent.name for layer in font.selectedLayers] or None)
