# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/36805750b888fba6.md
# this_file: ports/widgets/pyqt-official/sliders-36805750b888fba6.py

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


def build(qt):
    with S.Session(qt, "Synchronized sliders") as s:
        s.vertical()
        orientation = s.combo("orientation", ["Horizontal", "Vertical"])
        low = s.spin("minimum", -100, 100, 0)
        high = s.spin("maximum", -100, 100, 20)
        number = s.spin("value", -100, 100, 5)
        controls = []
        busy = [False]
        for key, kind in [
            ("slider", "QSlider"),
            ("scrollbar", "QScrollBar"),
            ("dial", "QDial"),
        ]:
            obj = s.keep(key, getattr(s.g, kind)(s.window))
            obj.setRange(0, 20)
            obj.setValue(5)
            s.add(obj)
            controls.append(obj)

        def sync(n):
            if busy[0]:
                return
            busy[0] = True
            try:
                bounded = max(
                    int(S.value(low, "value")), min(int(S.value(high, "value")), n)
                )
                for obj in controls + [number]:
                    obj.setValue(bounded)
                s.state["value"] = bounded
            finally:
                busy[0] = False

        def bounds(*a):
            minimum = int(S.value(low, "value"))
            maximum = max(minimum, int(S.value(high, "value")))
            high.setValue(maximum)
            for obj in controls:
                obj.setRange(minimum, maximum)
            sync(int(S.value(number, "value")))

        for obj in controls + [number]:
            s.link(obj, "valueChanged(int)", sync)
        s.link(low, "valueChanged(int)", bounds)
        s.link(high, "valueChanged(int)", bounds)
        s.link(
            orientation,
            "currentIndexChanged(int)",
            lambda i: [
                obj.setOrientation(s.c.Qt.Horizontal if i == 0 else s.c.Qt.Vertical)
                for obj in controls[:2]
            ],
        )
        for key, method in [
            ("appearance", "setInvertedAppearance"),
            ("keys", "setInvertedControls"),
        ]:
            box = s.check(key, "Invert " + key)
            s.link(
                box,
                "toggled(bool)",
                lambda flag, m=method: [getattr(obj, m)(flag) for obj in controls],
            )
        sync(5)
        return s.h
