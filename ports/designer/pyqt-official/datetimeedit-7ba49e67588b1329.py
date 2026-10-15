# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/7ba49e67588b1329.md
# this_file: ports/designer/pyqt-official/datetimeedit-7ba49e67588b1329.py

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
    with S.Session(qt, "Popup date editors") as s:
        s.vertical()
        for key, kind in [("date", "QDateEdit"), ("datetime", "QDateTimeEdit")]:
            edit = s.keep(key, getattr(s.g, kind)(s.window))
            edit.setCalendarPopup(True)
            edit.setDateTime(s.c.QDateTime.currentDateTime())
            s.add(edit)
            calendar = s.keep(key + "_calendar", edit.calendarWidget())

            def configure(options, cal=calendar):
                methods = {
                    "week_start": "setFirstDayOfWeek",
                    "grid": "setGridVisible",
                    "horizontal": "setHorizontalHeaderFormat",
                    "vertical": "setVerticalHeaderFormat",
                    "navigation": "setNavigationBarVisible",
                }
                for name, val in options.items():
                    getattr(cal, methods[name])(val)

            def reset(cal=calendar):
                cal.setFirstDayOfWeek(s.c.Qt.Monday)
                cal.setGridVisible(False)
                cal.setNavigationBarVisible(True)
                cal.setHorizontalHeaderFormat(s.g.QCalendarWidget.ShortDayNames)
                cal.setVerticalHeaderFormat(s.g.QCalendarWidget.ISOWeekNumbers)

            s.keep("configure_" + key, configure)
            s.keep("reset_" + key, reset)
        return s.h
