# MenuTitle: GetGo - Widen Two Glyphs
# SPDX-License-Identifier: Apache-2.0
# this_file: examples/getgo/batch_transform.py
"""GG Baar (CC0-1.0): horizontally scale A/V nodes, anchors and advances.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Only the owned copy's default master changes.
Requires a dedicated FontLab session with no other documents; enforced by owned_font.
Scaling about x=0 scales left/right sidebearings along with outlines and advances.
"""

import math

from examples.getgo._shared import notify, owned_font, required_layer


def transformed(points: list[tuple], scale: float, shift: float) -> list[tuple]:
    """Horizontal affine transform in font units, retaining fractional precision."""
    if not math.isfinite(scale) or scale <= 0 or not math.isfinite(shift):
        raise ValueError("Scale must be finite and positive; shift must be finite")
    if any(not all(math.isfinite(n) for n in point) for point in points):
        raise ValueError("Points must be finite")
    return [(x * scale + shift, y) for x, y in points]


def run(scale: float = 1.1) -> dict:
    """Preflight the batch, transform its direct outlines and verify node readback."""
    from PythonQt.QtCore import QPointF

    transformed([], scale, 0)
    with owned_font("baar", mutates=True) as (package, record):
        targets = [required_layer(package, name) for name in ("A", "V")]
        plans = []
        for glyph, layer in targets:
            if layer.components:
                raise ValueError(
                    f"This direct-outline transform cannot drop components: {glyph.name}"
                )
            nodes = [n for c in layer.getContours() for n in c.nodes()]
            if not nodes:
                raise ValueError(f"{glyph.name} needs a direct outline")
            plans.append(
                (
                    nodes,
                    transformed([(n.x, n.y) for n in nodes], scale, 0),
                    layer.advanceWidth,
                    [(a.name, a.point.x() * scale, a.point.y()) for a in layer.anchors],
                )
            )
        result = {}
        for (glyph, layer), (nodes, points, width, anchors) in zip(targets, plans):
            for node, (x, y) in zip(nodes, points):
                node.x, node.y = x, y
            for anchor in layer.anchors:
                anchor.point = QPointF(anchor.point.x() * scale, anchor.point.y())
            layer.advanceWidth = width * scale
        notify("GetGo horizontal scaling", targets)
        for (glyph, _), (_, points, width, anchors) in zip(targets, plans):
            _, readback = required_layer(package, glyph.name)
            fresh = [(n.x, n.y) for c in readback.getContours() for n in c.nodes()]
            actual_anchors = [
                (a.name, a.point.x(), a.point.y()) for a in readback.anchors
            ]
            if (
                any(
                    abs(ax - x) > 0.01 or abs(ay - y) > 0.01
                    for (ax, ay), (x, y) in zip(fresh, points)
                )
                or len(fresh) != len(points)
                or abs(readback.advanceWidth - width * scale) > 0.01
            ):
                raise AssertionError("Transformed coordinates differ")
            if len(actual_anchors) != len(anchors) or any(
                name != expected_name or abs(x - ex) > 0.01 or abs(y - ey) > 0.01
                for (name, x, y), (expected_name, ex, ey) in zip(
                    actual_anchors, anchors
                )
            ):
                raise AssertionError("Transformed anchors differ")
            result[glyph.name] = {
                "before_width": width,
                "after_width": readback.advanceWidth,
                "points": len(fresh),
            }
        return {"source": record["page_url"], "scale": scale, "glyphs": result}


if __name__ == "__main__":
    print(run())
