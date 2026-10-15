# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/27bf65f8b059fd96.md
# this_file: ports/designer/pyqt-official/calculatorform-27bf65f8b059fd96.py

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
    with S.Session(qt, "Add two integers") as s:
        s.vertical()
        a = s.spin("first")
        s.label("+")
        b = s.spin("second")
        s.label("=")
        result = s.keep("result", s.label("0"))

        def update(*args):
            total = int(S.value(a, "value")) + int(S.value(b, "value"))
            result.setText(str(total))
            s.state["sum"] = total

        s.link(a, "valueChanged(int)", update)
        s.link(b, "valueChanged(int)", update)
        update()
        return s.h
