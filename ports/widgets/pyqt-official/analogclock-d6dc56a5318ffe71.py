# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/d6dc56a5318ffe71.md
# this_file: ports/widgets/pyqt-official/analogclock-d6dc56a5318ffe71.py

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

import datetime


def angles(hour, minute, second, offset=0):
    return ((hour + offset) % 12 + minute / 60) * 30, (minute + second / 60) * 6


def clock(qt, designer=False, shaped=False):
    with S.Session(qt, "Clock component" if designer else "Analog clock") as s:
        s.vertical()
        s.state.update(offset=0, notifications=[])
        now = [datetime.datetime.now()]
        drag = [None]

        def paint(p, w, h):
            edge = max(1, min(w, h))
            p.translate(w / 2, h / 2)
            p.scale(edge / 220, edge / 220)
            hour, minute = angles(
                now[0].hour, now[0].minute, now[0].second, s.state["offset"]
            )
            for angle, length, width, color in [
                (hour, 57, 7, "#3c9959" if designer else "#8553ad"),
                (minute, 83, 4, "#43a9a1"),
            ]:
                p.save()
                p.rotate(angle)
                p.setPen(s.g.QColor(color))
                p.setBrush(s.g.QColor(color))
                points = s.g.QPolygon(
                    [
                        s.c.QPoint(-width, 10),
                        s.c.QPoint(width, 10),
                        s.c.QPoint(0, -length),
                    ]
                )
                p.drawPolygon(points)
                p.restore()
            p.setPen(s.g.QColor("#42515b"))
            for i in range(60):
                p.save()
                p.rotate(i * 6)
                p.drawLine(0, -98, 0, -88 if i % 5 == 0 else -94)
                p.restore()

        def press(event):
            if event.button() == s.c.Qt.LeftButton:
                pos = event.globalPos()
                drag[0] = (
                    int(S.value(pos, "x")) - int(S.value(s.window, "x")),
                    int(S.value(pos, "y")) - int(S.value(s.window, "y")),
                )

        def move(event):
            if drag[0] is not None and event.buttons() & s.c.Qt.LeftButton:
                pos = event.globalPos()
                s.window.move(
                    int(S.value(pos, "x")) - drag[0][0],
                    int(S.value(pos, "y")) - drag[0][1],
                )

        def mask(*args):
            w = int(S.value(s.window, "width"))
            h = int(S.value(s.window, "height"))
            edge = min(w, h)
            s.window.setMask(
                s.g.QRegion(
                    (w - edge) // 2, (h - edge) // 2, edge, edge, s.g.QRegion.Ellipse
                )
            )

        def context(event):
            menu = s.g.QMenu(s.window)
            action = s.g.QAction("Exit", s.window)
            menu.addAction(action)
            s.link(action, "triggered()", lambda *a: s.h.close())
            s.keep("context_menu", menu)
            menu.popup(event.globalPos())

        face = S.canvas(
            s,
            paint,
            {
                "press": press,
                "move": move,
                "release": lambda e: drag.__setitem__(0, None),
                "resize": mask,
                "context": context,
            }
            if shaped
            else {},
        )
        s.add(face)
        if shaped:
            s.window.setWindowFlags(s.c.Qt.FramelessWindowHint)
            mask()

        def tick():
            now[0] = datetime.datetime.now()
            s.state["local_time"] = now[0].isoformat()
            if designer:
                s.state["notifications"] = (
                    s.state["notifications"] + [now[0].isoformat()]
                )[-64:]
            face.update()

        def offset(hours):
            s.state["offset"] = int(hours)
            face.update()

        s.keep("set_offset", offset)
        s.keep("reset", lambda: offset(0))
        s.timer("clock_timer", 1000, tick)
        tick()
        return s.h


def build(qt):
    return clock(qt)
