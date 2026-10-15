# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/773db5c24ae98ffb.md
# this_file: ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py

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


def vertices(points, inner, outer, rotation):
    points = max(3, int(points))
    angle = math.radians(max(0, min(360, rotation)))
    return [
        (
            math.cos(angle + i * math.pi / points) * (outer if i % 2 == 0 else inner),
            math.sin(angle + i * math.pi / points) * (outer if i % 2 == 0 else inner),
        )
        for i in range(points * 2)
    ]


def build(qt):
    with S.Session(qt, "Star polygon component") as s:
        s.vertical()
        s.state.update(
            points=5,
            inner=40.0,
            outer=90.0,
            rotation=0.0,
            inner_color="#fff4bd",
            outer_color="#315b91",
        )

        def paint(p, w, h):
            p.translate(w / 2, h / 2)
            scale = min(w, h) / 220
            p.scale(scale, scale)
            gradient = s.g.QRadialGradient(0.0, 0.0, max(1.0, s.state["outer"]))
            gradient.setColorAt(0, s.g.QColor(s.state["inner_color"]))
            gradient.setColorAt(1, s.g.QColor(s.state["outer_color"]))
            p.setBrush(s.g.QBrush(gradient))
            polygon = s.g.QPolygonF(
                [
                    s.c.QPointF(x, y)
                    for x, y in vertices(
                        s.state["points"],
                        s.state["inner"],
                        s.state["outer"],
                        s.state["rotation"],
                    )
                ]
            )
            p.drawPolygon(polygon)

        face = S.canvas(s, paint)
        s.add(face)

        def change(key, val):
            if key.endswith("color"):
                color = s.g.QColor(val)
                if not color.isValid():
                    raise ValueError("Choose a valid color")
                val = str(color.name())
            elif key == "points":
                val = max(3, min(100, int(val)))
            elif key == "rotation":
                val = max(0.0, min(360.0, float(val)))
            else:
                val = max(0.0, float(val))
            s.state[key] = val
            face.update()

        for key in list(s.state):
            s.keep("set_" + key, lambda val, k=key: change(k, val))
        return s.h
