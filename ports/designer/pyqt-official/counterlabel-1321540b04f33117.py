# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/1321540b04f33117.md
# this_file: ports/designer/pyqt-official/counterlabel-1321540b04f33117.py

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
    with S.Session(qt, "Counter component") as s:
        s.vertical()
        s.state.update(minimum=1, maximum=1, value=1, offset=0, notifications=[])

        def paint(p, w, h):
            font = s.g.QFont(S.value(s.window, "font"))
            font.setPixelSize(
                max(1, min(h, int(w / max(1, len(str(s.state["maximum"]))))))
            )
            p.setFont(font)
            p.drawText(0, 0, w, h, s.c.Qt.AlignCenter, str(s.state["value"]))

        face = S.canvas(s, paint)
        s.add(face)

        def change(key, n):
            n = int(n)
            if key == "value" and not s.state["minimum"] <= n <= s.state["maximum"]:
                return False
            if key == "minimum" and n > s.state["maximum"]:
                return False
            if key == "maximum" and n < s.state["minimum"]:
                return False
            s.state[key] = n
            if key == "value":
                emitted = n + s.state["offset"]
                s.state["notifications"].append([emitted, str(emitted)])
            face.update()
            return True

        for key in ["minimum", "maximum", "value", "offset"]:
            s.keep("set_" + key, lambda n, k=key: change(k, n))
        s.keep("step_up", lambda: change("value", s.state["value"] + 1))
        s.keep("step_down", lambda: change("value", s.state["value"] - 1))
        s.keep("set_font", face.setFont)
        change("value", 123)
        return s.h
