# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/e62ce3eb648cfb4c.md
# this_file: ports/widgets/pyqt-official/tooltips-e62ce3eb648cfb4c.py

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

import random


def hit(shapes, x, y):
    for index in range(len(shapes) - 1, -1, -1):
        kind, cx, cy, r, _color = shapes[index]
        dx = x - cx
        dy = y - cy
        inside = (
            dx * dx + dy * dy <= r * r
            if kind == "Circle"
            else abs(dx) <= r and abs(dy) <= r
            if kind == "Square"
            else -r <= dy <= r and abs(dx) <= (dy + r) / 2
        )
        if inside:
            return index
    return None


def build(qt):
    with S.Session(qt, "Shapes and hover help") as s:
        s.vertical()
        rng = random.Random()
        shapes = []
        drag = [None]

        def paint(p, w, h):
            for kind, x, y, r, color in shapes:
                p.setBrush(s.g.QColor(color))
                if kind == "Circle":
                    p.drawEllipse(s.c.QPointF(x, y), r, r)
                elif kind == "Square":
                    p.drawRect(int(x - r), int(y - r), int(r * 2), int(r * 2))
                else:
                    p.drawPolygon(
                        s.g.QPolygonF(
                            [
                                s.c.QPointF(x, y - r),
                                s.c.QPointF(x + r, y + r),
                                s.c.QPointF(x - r, y + r),
                            ]
                        )
                    )

        def coordinates(event):
            pos = event.pos()
            return float(S.value(pos, "x")), float(S.value(pos, "y"))

        def press(event):
            if event.button() != s.c.Qt.LeftButton:
                return
            x, y = coordinates(event)
            index = hit(shapes, x, y)
            if index is not None:
                shape = shapes.pop(index)
                shapes.append(shape)
                drag[0] = (shape, x - shape[1], y - shape[2])

        def move(event):
            x, y = coordinates(event)
            if drag[0] is not None and event.buttons() & s.c.Qt.LeftButton:
                shape, dx, dy = drag[0]
                shape[1] = x - dx
                shape[2] = y - dy
                face.update()
            else:
                index = hit(shapes, x, y)
                if index is not None:
                    s.g.QToolTip.showText(
                        event.globalPos(), shapes[index][0] + " — drag to move", face
                    )

        face = S.canvas(
            s,
            paint,
            {
                "press": press,
                "move": move,
                "release": lambda e: drag.__setitem__(0, None),
            },
        )
        s.add(face)

        def create(kind):
            width = max(1, int(S.value(face, "width")))
            height = max(1, int(S.value(face, "height")))
            shapes.append(
                [
                    kind,
                    rng.uniform(0, width),
                    rng.uniform(0, height),
                    24.0,
                    rng.choice(["#609caf", "#bd8955", "#8c78b6"]),
                ]
            )
            face.update()
            s.state["count"] = len(shapes)

        for kind in ["Circle", "Square", "Triangle"]:
            button = s.button(kind, kind, lambda k=kind: create(k))
            icon = s.g.QPixmap(32, 32)
            icon.fill(s.g.QColor(0, 0, 0, 0))
            painter = s.g.QPainter(icon)
            try:
                painter.setBrush(s.g.QColor("#609caf"))
                if kind == "Circle":
                    painter.drawEllipse(4, 4, 24, 24)
                elif kind == "Square":
                    painter.drawRect(4, 4, 24, 24)
                else:
                    painter.drawPolygon(
                        s.g.QPolygon(
                            [s.c.QPoint(16, 3), s.c.QPoint(29, 28), s.c.QPoint(3, 28)]
                        )
                    )
            finally:
                painter.end()
            button.setIcon(s.g.QIcon(icon))
            create(kind)
        s.keep("shapes", shapes)
        s.keep("create", create)
        return s.h
