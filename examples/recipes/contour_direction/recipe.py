#MenuTitle: Correct Contour Direction and Start Points
# this_file: examples/recipes/contour_direction/recipe.py
"""PostScript contour direction and bottom-left start points for the current master.

Outer contours run counter-clockwise and counters clockwise (the PostScript/CFF
convention, in FontLab's y-up coordinates); nesting decides which is which.
Each contour then starts at its lowest, then leftmost on-curve node. Orientation
(signed area of the flattened outline) and nesting (an exact ray-crossing test on
the Bézier segments themselves) come from the actual outline, not from the
control points and not from FontLab.
"""

FLATTEN_STEPS = 16  # for the signed area only; containment does not flatten
MAX_DEPTH = 48  # subdivision depth bound: segments shorter than ~2**-48 units


def _cubic(p0, p1, p2, p3, steps):
    return [
        tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d
              for a, b, c, d in zip(p0, p1, p2, p3))
        for t in (i / steps for i in range(1, steps + 1))
    ]


def _quad(p0, p1, p2, steps):
    return [
        tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * c for a, b, c in zip(p0, p1, p2))
        for t in (i / steps for i in range(1, steps + 1))
    ]


def _mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def segments(points: list, on_curve: list[bool]) -> list[tuple]:
    """Segments of a closed outline as control-point tuples: 2 points for a line, 3
    for a quadratic, 4 for a cubic. Two off-curve points between on-curve points make
    a cubic; one or more make TrueType quadratics with implied on-curve midpoints."""
    points, on_curve = [tuple(p) for p in points], list(on_curve)
    if not any(on_curve):  # all off-curve (a TrueType circle): add one implied point
        points.insert(0, _mid(points[-1], points[0]))
        on_curve.insert(0, True)
    start = on_curve.index(True)
    points = points[start:] + points[:start]
    on_curve = on_curve[start:] + on_curve[:start]
    current, result, handles = points[0], [], []
    for point, on in zip(points[1:] + points[:1], on_curve[1:] + [True]):
        if not on:
            handles.append(point)
            continue
        if len(handles) == 2:
            result.append((current, handles[0], handles[1], point))
        elif handles:
            for k, handle in enumerate(handles):
                end = point if k == len(handles) - 1 else _mid(handle, handles[k + 1])
                result.append((current, handle, end))
                current = end
        elif point != current:
            result.append((current, point))
        current, handles = point, []
    return result


def flatten(points: list, on_curve: list[bool], steps: int = FLATTEN_STEPS) -> list:
    """Polygon along a closed outline (see ``segments``), for its signed area."""
    polygon = []
    for segment in segments(points, on_curve):
        polygon.append(segment[0])
        if len(segment) == 4:
            polygon += _cubic(*segment, steps)[:-1]
        elif len(segment) == 3:
            polygon += _quad(*segment, steps)[:-1]
    return polygon


def signed_area(points: list[tuple[float, float]]) -> float:
    """Shoelace area in y-up coordinates: positive means counter-clockwise."""
    pairs = zip(points, points[1:] + points[:1])
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in pairs) / 2


def _split(segment: tuple) -> tuple[tuple, tuple]:
    """de Casteljau halves of a Bézier segment of any degree."""
    left, right, row = [segment[0]], [segment[-1]], list(segment)
    while len(row) > 1:
        row = [_mid(a, b) for a, b in zip(row, row[1:])]
        left.append(row[0])
        right.append(row[-1])
    return tuple(left), tuple(reversed(right))


def _crossings(segment: tuple, x: float, y: float, depth: int = 0) -> int:
    """Parity of the crossings of the ray from (x, y) towards +x with ``segment``.

    Exact for curves: a segment's control hull bounds it, so a hull wholly beside,
    above or below the ray decides by its end points alone; otherwise subdivide.
    """
    (x0, y0), (x1, y1) = segment[0], segment[-1]
    xs, ys = [p[0] for p in segment], [p[1] for p in segment]
    straddles = (y0 > y) != (y1 > y)
    if min(ys) > y or max(ys) <= y or max(xs) <= x:
        return 0  # wholly above, below or left of the ray
    if min(xs) > x:
        return int(straddles)  # wholly right: a continuous curve crosses with end-point parity
    if len(segment) == 2 or depth >= MAX_DEPTH:
        return int(straddles and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    left, right = _split(segment)
    return _crossings(left, x, y, depth + 1) ^ _crossings(right, x, y, depth + 1)


def contains(contour: list[tuple], point: tuple[float, float]) -> bool:
    """Even-odd ray test against the segments of ``contour`` (see ``segments``)."""
    x, y = point
    inside = 0
    for segment in contour:
        inside ^= _crossings(segment, x, y)
    return bool(inside)


def wants_counter_clockwise(contours: list[list[tuple]], index: int) -> bool:
    """Outer (even nesting depth) contours run counter-clockwise; ``contours`` are
    segment lists."""
    probe = contours[index][0][0]
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


def _reversed_order(items: list) -> list:
    """Node order after flContour.reverse(): the first node stays, the rest reverse."""
    return items[:1] + items[1:][::-1]


def plan(glyph_name: str, contours: list) -> tuple[list, list]:
    """Edits for one layer's closed contours, computed without touching them.

    Returns ``(edits, skipped)``: edits are ``(contour, reverse, start)`` tuples;
    contours with no segments (one node, or all on-curve nodes coincident) have no
    direction and are skipped and reported instead.
    """
    outlines = [([(n.x, n.y) for n in c.nodes()], [n.isOn() for n in c.nodes()]) for c in contours]
    shapes = [segments(*outline) for outline in outlines]
    usable = [i for i, shape in enumerate(shapes) if shape]
    skipped = [{"glyph": glyph_name, "contour": i} for i in range(len(contours)) if not shapes[i]]
    edits = []
    for k, index in enumerate(usable):
        points, on_curve = outlines[index]
        ccw = signed_area(flatten(points, on_curve)) > 0
        reverse = ccw != wants_counter_clockwise([shapes[i] for i in usable], k)
        if reverse:
            points, on_curve = _reversed_order(points), _reversed_order(on_curve)
        start = start_index(points, on_curve)
        if reverse or start:
            edits.append((contours[index], reverse, start))
    return edits, skipped


def run(font_id=None, glyph_names=None, master=None) -> dict:
    """Fix direction and start point of every closed contour; returns what changed.

    Every layer is read and planned before the first edit, so an unreadable glyph
    or contour leaves the font unchanged.
    """
    import fontlab

    package, glyphs = _targets(font_id, glyph_names)
    master = master or package.master
    planned, skipped = [], []
    for glyph in glyphs:
        layer = glyph.findLayer(master)
        if layer is None:
            continue
        edits, missed = plan(glyph.name, [c for c in layer.getContours() if c.closed])
        skipped += missed
        if edits:
            planned.append((glyph, layer, edits))
    reversed_ = restarted = 0
    for _glyph, _layer, edits in planned:
        for contour, reverse, start in edits:
            if reverse:
                contour.reverse()
                reversed_ += 1
            if start:
                contour.setStartPoint(start)
                restarted += 1
    if planned:
        layers, changed = [p[1] for p in planned], [p[0] for p in planned]
        fontlab.flItems().notifyChangesApplied("Correct contour direction", layers + changed)
    return {"master": master, "reversed": reversed_, "restarted": restarted,
            "glyphs": [p[0].name for p in planned], "skipped": skipped}


# Menu use: name glyphs, then run the script. Nothing happens while GLYPHS is empty.
GLYPHS = []  # e.g. ["A", "B"]

if __name__ == "__main__":
    if GLYPHS:
        print(run(glyph_names=GLYPHS))
    else:
        print("Correct Contour Direction: set GLYPHS at the end of this script first.")
