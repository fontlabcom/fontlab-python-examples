# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/dc59f268ee01e364.md
# this_file: ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py

import importlib.util
import sys
from pathlib import Path

_key = "fontlab_cleanroom_a_primitives"
if _key not in sys.modules:
    _path = (
        Path(__file__).resolve().parents[2]
        / "layouts/pyqt-official/basiclayouts-2f94fe07de765888.py"
    )
    _spec = importlib.util.spec_from_file_location(_key, _path)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_key] = _module
    try:
        _spec.loader.exec_module(_module)
    except BaseException:
        sys.modules.pop(_key, None)
        raise
S = sys.modules[_key]

import math


def rating_at(x, width, maximum=5):
    return max(0, min(maximum, int(maximum * x / max(1, width)) + 1))


def build(qt):
    with S.Session(qt, "Star rating delegate") as s:
        s.vertical()
        model = s.model(
            ["Title", "Performer", "Rating"],
            [
                ["Morning walk", "Paper quartet", 3],
                ["Evening rain", "Quiet trio", 4],
                ["First light", "Window ensemble", 2],
                ["Open road", "Small band", 5],
            ],
        )
        view = s.view("table", model)

        def draw(p, rect, rating):
            x = int(S.value(rect, "x"))
            y = int(S.value(rect, "y"))
            w = int(S.value(rect, "width"))
            h = int(S.value(rect, "height"))
            cell = w / 5
            for i in range(5):
                p.setBrush(s.g.QColor("#e7b43d" if i < rating else "#e3e6eb"))
                points = []
                for vertex in range(10):
                    angle = vertex * math.pi / 5 - math.pi / 2
                    radius = min(cell, h) * (0.44 if vertex % 2 == 0 else 0.2)
                    points.append(
                        s.c.QPointF(
                            x + (i + 0.5) * cell + math.cos(angle) * radius,
                            y + h / 2 + math.sin(angle) * radius,
                        )
                    )
                p.drawPolygon(s.g.QPolygonF(points))

        class Delegate(s.g.QStyledItemDelegate):
            def paint(self, p, option, index):
                if index.column() != 2:
                    return s.g.QStyledItemDelegate.paint(self, p, option, index)
                draw(p, option.rect, int(model.data(index, s.c.Qt.EditRole)))

            def createEditor(self, parent, option, index):
                if index.column() != 2:
                    return s.g.QStyledItemDelegate.createEditor(
                        self, parent, option, index
                    )
                state = {"value": int(model.data(index, s.c.Qt.EditRole))}

                class Editor(s.g.QWidget):
                    def paintEvent(self, event):
                        p = s.g.QPainter(self)
                        try:
                            draw(p, self.rect(), state["value"])
                        finally:
                            p.end()

                    def mouseMoveEvent(self, event):
                        state["value"] = rating_at(
                            int(S.value(event.pos(), "x")), int(S.value(self, "width"))
                        )
                        self.update()

                    def mouseReleaseEvent(self, event):
                        state["value"] = rating_at(
                            int(S.value(event.pos(), "x")), int(S.value(self, "width"))
                        )
                        editors[id(self)] = state
                        delegate.commitData(self)
                        delegate.closeEditor(self, s.g.QAbstractItemDelegate.NoHint)

                editor = Editor(parent)
                editor.setMouseTracking(True)
                editors[id(editor)] = state
                return editor

            def setEditorData(self, editor, index):
                if index.column() != 2:
                    return s.g.QStyledItemDelegate.setEditorData(self, editor, index)
                editors[id(editor)]["value"] = int(model.data(index, s.c.Qt.EditRole))

            def setModelData(self, editor, target, index):
                if index.column() != 2:
                    return s.g.QStyledItemDelegate.setModelData(
                        self, editor, target, index
                    )
                target.setData(index, editors[id(editor)]["value"], s.c.Qt.EditRole)

        editors = {}
        delegate = s.keep("delegate", Delegate(view))
        view.setItemDelegateForColumn(2, delegate)
        s.h.release.append(editors.clear)
        return s.h
