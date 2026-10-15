# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/3040b9f6b267a196.md
# this_file: ports/widgets/pyqt-official/digitalclock-3040b9f6b267a196.py

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

from datetime import datetime


def display_time(hour, minute, second):
    return f"{hour:02d}" + (":" if second % 2 == 0 else " ") + f"{minute:02d}"


def build(qt):
    with S.Session(qt, "Digital clock") as s:
        s.vertical()
        lcd = s.keep("lcd", s.g.QLCDNumber(s.window))
        lcd.setDigitCount(5)
        lcd.setSegmentStyle(s.g.QLCDNumber.Filled)
        s.add(lcd)

        def tick():
            now = datetime.now()
            text = display_time(now.hour, now.minute, now.second)
            s.state["display"] = text
            lcd.display(text)

        s.timer("clock_timer", 1000, tick)
        tick()
        return s.h
