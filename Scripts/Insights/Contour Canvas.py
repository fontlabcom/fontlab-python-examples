# this_file: Scripts/Insights/Contour Canvas.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/kateliev_TypeRig/Scripts/TypeRig Tools/TR-DeltaPreview.py:21 — source licence unresolved; see catalog/insights.json.
"""Demonstrate contour canvas with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    with S.Session(qt, "Synthetic contour — QPainterPath") as session:
        session.vertical()
        path = qt.QtGui.QPainterPath()
        path.moveTo(60.0, 210.0)
        path.lineTo(60.0, 90.0)
        path.cubicTo(60.0, 25.0, 230.0, 25.0, 230.0, 90.0)
        path.lineTo(230.0, 210.0)
        path.closeSubpath()
        session.state.update(paint_count=0, path_elements=path.elementCount(), synthetic=True)

        def paint(painter, width, height):
            painter.drawPath(path)
            session.state["paint_count"] += 1

        session.add(S.canvas(session, paint))
        return session.h


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_contour-canvas", "Contour Canvas")


if __name__ == "__main__":
    main()
