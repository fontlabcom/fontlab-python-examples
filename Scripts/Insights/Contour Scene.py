# this_file: Scripts/Insights/Contour Scene.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/knossos-project_knossos/python/examples/graphics_view.py:6 — source licence unresolved; see catalog/insights.json.
"""Demonstrate contour scene with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with S.Session(qt, "Synthetic contour — graphics scene", gui.QWidget()) as session:
        handle = session.h
        window = handle.widget
        scene = gui.QGraphicsScene(window)
        path = gui.QPainterPath()
        path.moveTo(40.0, 180.0)
        path.lineTo(100.0, 30.0)
        path.lineTo(160.0, 180.0)
        path.closeSubpath()
        scene.addPath(path, gui.QPen(), gui.QBrush())
        scene.addLine(0.0, 180.0, 220.0, 180.0, gui.QPen())
        scene.addLine(200.0, 0.0, 200.0, 210.0, gui.QPen())
        view = gui.QGraphicsView(scene, window)
        view.setSceneRect(-20.0, -20.0, 400.0, 400.0)
        view.setDragMode(gui.QGraphicsView.ScrollHandDrag)
        gui.QVBoxLayout(window).addWidget(view)
        handle.controls.update(scene=scene, view=view)
        handle.inspect_ui = lambda: {
            "item_count": len(scene.items()),
            "path_elements": path.elementCount(),
            "guides": ["baseline", "advance"],
            "synthetic": True,
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_contour-scene", "Contour Scene")


if __name__ == "__main__":
    main()
