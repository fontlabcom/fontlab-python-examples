# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/9941e3c752b3a3b7.md
# this_file: ports/designer/pyqt-official/bubbleswidget-9941e3c752b3a3b7.py

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


def build(qt):
    with S.Session(qt, "Bubble component") as s:
        s.vertical()
        rng = random.Random()
        bubbles = []
        growing = [None]
        s.state.update(
            count=10,
            inner="#d3efff",
            outer="#317caf",
            description="Floating bubbles",
            running=True,
        )

        def paint(p, w, h):
            for x, y, r in bubbles:
                gradient = s.g.QRadialGradient(float(x), float(y), max(1.0, r))
                gradient.setColorAt(0, s.g.QColor(s.state["inner"]))
                gradient.setColorAt(1, s.g.QColor(s.state["outer"]))
                p.setBrush(s.g.QBrush(gradient))
                p.drawEllipse(s.c.QPointF(x, y), r, r)

        def press(event):
            point = event.pos()
            bubble = [float(S.value(point, "x")), float(S.value(point, "y")), 3.0]
            bubbles.append(bubble)
            growing[0] = bubble
            grow.start(30)

        def release(event):
            growing[0] = None
            grow.stop()

        face = S.canvas(s, paint, {"press": press, "release": release})
        s.add(face)

        def growth():
            if growing[0] is not None:
                growing[0][2] = min(150.0, growing[0][2] + 1)
                face.update()

        def motion():
            height = max(1, int(S.value(face, "height")))
            width = max(1, int(S.value(face, "width")))
            while len(bubbles) < s.state["count"]:
                bubbles.append(
                    [rng.uniform(0, width), rng.uniform(0, height), rng.uniform(8, 25)]
                )
            active = growing[0]
            idle = [bubble for bubble in bubbles if bubble is not active]
            idle = idle[: max(0, s.state["count"] - (1 if active is not None else 0))]
            bubbles[:] = idle + ([active] if active is not None else [])
            for bubble in bubbles:
                if bubble is not growing[0]:
                    bubble[1] -= 1.0
                    bubble[1] = (
                        height + bubble[2] if bubble[1] + bubble[2] < 0 else bubble[1]
                    )
            face.update()
            s.state["bubbles"] = [list(b) for b in bubbles]

        grow = s.timer("growth_timer", 30, growth, start=False)
        move = s.timer("motion_timer", 30, motion)

        def running(flag):
            s.state["running"] = bool(flag)
            if flag:
                move.start(30)
            else:
                move.stop()
                grow.stop()

        def configure(key, val):
            if key == "count":
                val = max(0, min(200, int(val)))
            elif key in ["inner", "outer"]:
                color = s.g.QColor(val)
                if not color.isValid():
                    raise ValueError("Invalid bubble color")
                val = str(color.name())
            s.state[key] = val
            face.update()

        for key in ["count", "inner", "outer", "description"]:
            s.keep("set_" + key, lambda val, k=key: configure(k, val))
        s.keep("start", lambda: running(True))
        s.keep("stop", lambda: running(False))
        return s.h
