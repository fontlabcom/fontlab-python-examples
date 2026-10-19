# this_file: lessons/src/fontlab_python_lessons/getgo/spacing.py
# SPDX-License-Identifier: Apache-2.0
# MenuTitle: GetGo - Sidebearings from H

"""GG Baar (CC0-1.0): give I the left and right sidebearings of H.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Changes are discarded when the owned copy closes.
Requires a dedicated FontLab session with no other documents; enforced by owned_font.
"""

import math

from fontlab_python_lessons.getgo._shared import notify, owned_font, required_layer


def spacing_plan(left: float, right: float, lsb: float, rsb: float) -> dict:
    """Compute outline shift and advance; negative sidebearings are allowed."""
    if not all(math.isfinite(v) for v in (left, right, lsb, rsb)) or right < left:
        msg = "Expected finite sidebearings and ordered bounds"
        raise ValueError(msg)
    return {"shift": lsb - left, "width": lsb + right - left + rsb}


def run() -> dict:
    """Move direct outline nodes and anchors, set width, then read bearings back."""
    from PythonQt.QtCore import QPointF

    with owned_font("baar", mutates=True) as (package, record):
        _, reference = required_layer(package, "H")
        glyph, target = required_layer(package, "I")
        if reference.components or target.components:
            msg = "This direct-outline example requires component-free H/I"
            raise ValueError(msg)
        if not reference.getContours() or not target.getContours():
            msg = "H and I must have direct contours"
            raise ValueError(msg)
        box, original = reference.boundingBox, target.boundingBox
        lsb, rsb = box.x(), reference.advanceWidth - box.x() - box.width()
        plan = spacing_plan(original.x(), original.x() + original.width(), lsb, rsb)
        for contour in target.getContours():
            for node in contour.nodes():
                node.x += plan["shift"]
        for anchor in target.anchors:
            anchor.point = QPointF(anchor.point.x() + plan["shift"], anchor.point.y())
        target.advanceWidth = plan["width"]
        notify("GetGo sidebearings", [(glyph, target)])
        _, readback = required_layer(package, "I")
        # GG Baar I is a straight-line, component-free outline. Native cached
        # boundingBox/contourRect stay stale after node edits; re-read the nodes.
        xs = [node.x for contour in readback.getContours() for node in contour.nodes()]
        if not xs:
            msg = "I has no read-back outline nodes"
            raise AssertionError(msg)
        bearings = [min(xs), readback.advanceWidth - max(xs)]
        if any(abs(a - b) > 0.01 for a, b in zip(bearings, (lsb, rsb), strict=False)):
            msg = "Sidebearing readback differs from the plan"
            raise AssertionError(msg)
        return {
            "source": record["page_url"],
            "glyph": "I",
            "reference": "H",
            "plan": plan,
            "sidebearings": bearings,
        }
