# this_file: ports/insights/contour-scene.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/knossos-project_knossos/python/examples/graphics_view.py:6 — source licence unresolved; see catalog/insights.json.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with owned(gui.QWidget(), "Synthetic contour — graphics scene") as handle:
        window = handle.widget
        scene = gui.QGraphicsScene(window)
        path = gui.QPainterPath()
        path.moveTo(40.0, 180.0)
        path.lineTo(100.0, 30.0)
        path.lineTo(160.0, 180.0)
        path.closeSubpath()
        scene.addPath(path)
        scene.addLine(0.0, 180.0, 220.0, 180.0)
        scene.addLine(200.0, 0.0, 200.0, 210.0)
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


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("contour-scene")
