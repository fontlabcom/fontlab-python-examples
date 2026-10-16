# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/468179092748a72e.md
# this_file: ports/widgets/pyqt-official/spinboxes-468179092748a72e.py

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
    with S.Session(qt, "Numeric and date editors") as s:
        s.vertical()
        s.spin("integer", -20, 20, 0)
        zoom = s.spin("zoom", 0, 1000, 100)
        zoom.setSuffix("%")
        currency = s.spin("currency", 0, 999, 25)
        currency.setPrefix("$")
        decimal = []
        for key, pre, suf in [
            ("decimal", "", ""),
            ("percent", "", "%"),
            ("money", "$", ""),
        ]:
            obj = s.spin(key, -1000, 1000, 12.34, decimal=True)
            obj.setPrefix(pre)
            obj.setSuffix(suf)
            decimal.append(obj)
        precision = s.spin("precision", 0, 100, 2)
        s.link(
            precision,
            "valueChanged(int)",
            lambda n: [obj.setDecimals(n) for obj in decimal],
        )
        for key, kind in [
            ("date", "QDateEdit"),
            ("time", "QTimeEdit"),
            ("meeting", "QDateTimeEdit"),
        ]:
            obj = s.keep(key, getattr(s.g, kind)(s.window))
            s.add(obj)
            obj.setDateTime(s.c.QDateTime.currentDateTime())
        meeting = s.controls["meeting"]
        meeting.setDateTimeRange(
            s.c.QDateTime(s.c.QDate(2020, 1, 1)), s.c.QDateTime(s.c.QDate(2040, 12, 31))
        )
        fmt = s.combo("format", ["yyyy-MM-dd hh:mm", "dd MMM yyyy", "hh:mm AP"])
        s.link(
            fmt,
            "currentIndexChanged(int)",
            lambda i: meeting.setDisplayFormat(
                ["yyyy-MM-dd hh:mm", "dd MMM yyyy", "hh:mm AP"][i]
            ),
        )
        s.label("Meeting range: 2020–2040. Precision: 0–100 decimal places.")
        return s.h
