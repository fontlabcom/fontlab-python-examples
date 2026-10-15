# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b823a76f79197d84.md
# this_file: ports/effects/pyqt-official/lighting-b823a76f79197d84.py

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


def build(qt):
    with S.Session(qt, "Moving light and soft shadows") as s:
        s.vertical()
        scene = s.keep("scene", s.g.QGraphicsScene(s.window))
        view = s.keep("view", s.g.QGraphicsView(scene, s.window))
        s.add(view)
        scene.setSceneRect(0.0, 0.0, 500.0, 500.0)
        shadows = []
        for row in range(5):
            for col in range(5):
                x = 55 + col * 85
                y = 55 + row * 85
                gradient = s.g.QLinearGradient(0.0, 0.0, 0.0, 35.0)
                gradient.setColorAt(
                    0, s.g.QColor.fromHsv((row * 60 + col * 20) % 360, 120, 245)
                )
                gradient.setColorAt(1, s.g.QColor("#45536a"))
                item = s.g.QGraphicsRectItem(float(x), float(y), 35.0, 35.0)
                item.setPen(s.g.QPen(s.g.QColor("#53627b")))
                item.setBrush(s.g.QBrush(gradient))
                scene.addItem(item)
                effect = s.g.QGraphicsDropShadowEffect(view)
                effect.setBlurRadius(15.0)
                item.setGraphicsEffect(effect)
                shadows.append((x + 17, y + 17, effect))
        light = s.g.QGraphicsEllipseItem(0.0, 0.0, 22.0, 22.0)
        light.setBrush(s.g.QBrush(s.g.QColor("#fff7be")))
        scene.addItem(light)
        phase = [0.0]

        def tick():
            phase[0] = (phase[0] + 0.025) % (2 * math.pi)
            x = 250 + 205 * math.cos(phase[0])
            y = 250 + 205 * math.sin(phase[0])
            light.setPos(x - 11, y - 11)
            for cx, cy, effect in shadows:
                effect.setOffset((cx - x) / 14.0, (cy - y) / 14.0)
            s.state["light"] = [x, y]

        s.timer("light_timer", 30, tick)
        tick()
        return s.h
