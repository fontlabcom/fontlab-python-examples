# MenuTitle: GetGo - Outline Pens and Intersections
# SPDX-License-Identifier: Apache-2.0
# this_file: examples/getgo/outline_pens.py
"""GG Hint (Apache-2.0): exact curve bounds, signed areas and point counts.
Source font: https://code.fontlab.com/getgo-fonts/hint/
Original example code: Apache-2.0. Intersections are boundary tests, not boolean overlap.
"""

from itertools import combinations

from examples.getgo._pens import TuplePen
from examples.getgo._shared import owned_font, required_layer


def direction(area: float, closed: bool) -> str:
    """Y-up signed area labels; open and zero-area contours have no winding."""
    if not closed:
        return "open"
    return (
        "counter-clockwise" if area > 0 else "clockwise" if area < 0 else "degenerate"
    )


def contour_report(contour) -> dict:
    """Use segment pens, rather than treating off-curve nodes as a polygon."""
    from fontTools.pens.areaPen import AreaPen
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.recordingPen import RecordingPen, replayRecording

    recording = RecordingPen()
    try:
        contour.draw(TuplePen(recording))
    except AttributeError as exc:
        raise RuntimeError(
            "Native contour.draw did not emit the standard segment-pen protocol"
        ) from exc
    allowed = {"moveTo", "lineTo", "curveTo", "qCurveTo", "closePath", "endPath"}
    if not recording.value or any(op not in allowed for op, args in recording.value):
        raise ValueError("Expected nonempty component-free segment-pen recording")
    expected_end = "closePath" if contour.closed else "endPath"
    if recording.value[-1][0] != expected_end:
        raise ValueError("Native closed flag disagrees with segment-pen recording")
    bounds, area = BoundsPen(None), AreaPen()
    replayRecording(recording.value, bounds)
    if contour.closed:
        replayRecording(recording.value, area)
    return {
        "bounds": list(bounds.bounds) if bounds.bounds is not None else None,
        "points": len(contour.nodes()),
        "closed": bool(contour.closed),
        "signed_area": area.value if contour.closed else None,
        "direction": direction(area.value, contour.closed),
        "pen_protocol_verified": True,
    }


def run() -> dict:
    """Inspect A/B/O; contained counters do not count as intersecting boundaries."""
    with owned_font("hint") as (package, record):
        result = {}
        for name in ("A", "B", "O"):
            _, layer = required_layer(package, name)
            contours = list(layer.getContours())
            result[name] = {
                "contours": [contour_report(c) for c in contours],
                "intersecting_boundaries": [
                    [i, j]
                    for i, j in combinations(range(len(contours)), 2)
                    if contours[i].hasIntersPoints(contours[j])
                ],
            }
        return {"source": record["page_url"], "glyphs": result}


if __name__ == "__main__":
    print(run())
