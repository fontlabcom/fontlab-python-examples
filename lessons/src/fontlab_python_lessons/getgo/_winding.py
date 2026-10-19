# this_file: lessons/src/fontlab_python_lessons/getgo/_winding.py
# SPDX-License-Identifier: Apache-2.0
"""Compare each reopened contour's winding with its detached native source."""


def contour_signs(recording: list) -> list[int]:
    """Measure closed contours individually; cancellation cannot hide a reversal."""
    from fontTools.pens.areaPen import AreaPen
    from fontTools.pens.recordingPen import replayRecording

    signs, contour = [], []
    for operation in recording:
        contour.append(operation)
        if operation[0] == "closePath":
            pen = AreaPen()
            replayRecording(contour, pen)
            signs.append(1 if pen.value > 0 else -1 if pen.value < 0 else 0)
            contour = []
    if contour:
        msg = "Winding verification requires closed contours"
        raise ValueError(msg)
    return signs


def verify_winding(source: list, exported: list, is_ttf: bool) -> dict:
    """TTF conversion reverses each source contour; CFF preserves it."""
    original, actual = contour_signs(source), contour_signs(exported)
    expected = [-sign for sign in original] if is_ttf else original
    if actual != expected:
        msg = f"Exported contour winding differs: {actual} != {expected}"
        raise AssertionError(
            msg,
        )
    return {"source_signs": original, "export_signs": actual}
