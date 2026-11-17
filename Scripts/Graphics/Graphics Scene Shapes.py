# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Graphics/Graphics Scene Shapes.py
"""What: Put independently selectable and draggable paths in a QGraphicsScene.
Usage: Drag the coloured shapes. Ctrl-click to select more than one item.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is needed or changed. The scene owns all of its graphics items.
"""

from typing import Any


def populate(scene: Any, core: Any, gui: Any) -> None:
    """Use scene-owned items with Qt's built-in selection and movement."""
    for index, colour in enumerate(("#df8056", "#53aaa6", "#6694c2")):
        path = gui.QPainterPath()
        if index == 0:
            path.addEllipse(core.QRectF(0.0, 0.0, 110.0, 110.0))
        elif index == 1:
            path.addRoundedRect(core.QRectF(0.0, 0.0, 110.0, 110.0), 22.0, 22.0)
        else:
            path.moveTo(55.0, 0.0)
            path.lineTo(110.0, 110.0)
            path.lineTo(0.0, 110.0)
            path.closeSubpath()
        item = scene.addPath(path, gui.QPen(gui.QColor("#314758")), gui.QBrush(gui.QColor(colour)))
        item.setPos(25.0 + index * 145.0, 90.0)
        item.setFlag(gui.QGraphicsItem.ItemIsMovable, True)
        item.setFlag(gui.QGraphicsItem.ItemIsSelectable, True)


def main() -> Any:
    from PythonQt import QtCore, QtGui
    import fly.ap.core.scripting as scripting

    class View(QtGui.QGraphicsView):
        def __init__(self, parent: Any) -> None:
            QtGui.QGraphicsView.__init__(self, parent)
            self.setWindowFlags(QtCore.Qt.Window)
            self.setWindowTitle("Graphics Scene Shapes — drag to move")
            self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            self.resize(500, 350)
            self.shape_scene = QtGui.QGraphicsScene(self)
            self.shape_scene.setSceneRect(0.0, 0.0, 470.0, 300.0)
            self.setScene(self.shape_scene)
            self.setRenderHint(QtGui.QPainter.Antialiasing, True)
            populate(self.shape_scene, QtCore, QtGui)

    return scripting.show_script_dialog(View, "graphics_scene_shapes")


if __name__ == "__main__":
    main()
