# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b91effc45f81fbb0.md
# this_file: ports/widgets/pyqt-official/calendarwidget-b91effc45f81fbb0.py

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


def first_friday(year, month):
    return 1 + (4 - datetime.date(year, month, 1).weekday()) % 7


def build(qt):
    with S.Session(qt, "Calendar controls") as s:
        s.vertical()
        calendar = s.keep("calendar", s.g.QCalendarWidget(s.window))
        s.add(calendar)
        locale = s.combo("locale", ["en_US", "pl_PL", "de_DE"])
        week = s.combo("week", ["Monday", "Sunday"])
        selection = s.combo("selection", ["Single date", "None"])
        grid = s.check("grid", "Grid")
        navigation = s.check("navigation", "Navigation", True)
        horizontal = s.combo(
            "horizontal", ["Short names", "Long names", "Single letters", "None"]
        )
        vertical = s.combo("vertical", ["Week numbers", "None"])
        dates = []
        for key in ["selected", "minimum", "maximum"]:
            edit = s.keep(key, s.g.QDateEdit(s.window))
            s.add(edit)
            edit.setCalendarPopup(True)
            dates.append(edit)
        selected, minimum, maximum = dates
        selected.setDate(S.value(calendar, "selectedDate"))
        minimum.setDate(s.c.QDate(1900, 1, 1))
        maximum.setDate(s.c.QDate(2100, 12, 31))
        special = s.check("special", "Highlight first Friday and annual holiday")
        s.link(
            locale,
            "currentIndexChanged(int)",
            lambda i: calendar.setLocale(s.c.QLocale(["en_US", "pl_PL", "de_DE"][i])),
        )
        s.link(
            week,
            "currentIndexChanged(int)",
            lambda i: calendar.setFirstDayOfWeek(
                s.c.Qt.Monday if i == 0 else s.c.Qt.Sunday
            ),
        )
        s.link(
            selection,
            "currentIndexChanged(int)",
            lambda i: calendar.setSelectionMode(
                s.g.QCalendarWidget.SingleSelection
                if i == 0
                else s.g.QCalendarWidget.NoSelection
            ),
        )
        s.link(grid, "toggled(bool)", calendar.setGridVisible)
        s.link(navigation, "toggled(bool)", calendar.setNavigationBarVisible)
        s.link(
            horizontal,
            "currentIndexChanged(int)",
            lambda i: calendar.setHorizontalHeaderFormat(
                [
                    s.g.QCalendarWidget.ShortDayNames,
                    s.g.QCalendarWidget.LongDayNames,
                    s.g.QCalendarWidget.SingleLetterDayNames,
                    s.g.QCalendarWidget.NoHorizontalHeader,
                ][i]
            ),
        )
        s.link(
            vertical,
            "currentIndexChanged(int)",
            lambda i: calendar.setVerticalHeaderFormat(
                s.g.QCalendarWidget.ISOWeekNumbers
                if i == 0
                else s.g.QCalendarWidget.NoVerticalHeader
            ),
        )
        s.link(selected, "dateChanged(QDate)", calendar.setSelectedDate)
        s.link(
            calendar,
            "selectionChanged()",
            lambda *a: selected.setDate(S.value(calendar, "selectedDate")),
        )
        s.link(minimum, "dateChanged(QDate)", calendar.setMinimumDate)
        s.link(maximum, "dateChanged(QDate)", calendar.setMaximumDate)
        weekday = s.combo("weekday", ["Black", "Blue", "Green"])
        weekend = s.combo("weekend", ["Red", "Blue", "Black"])
        header = s.combo("header", ["Black", "Green", "Blue"])
        old = []

        def formats(*args):
            for day in range(1, 8):
                fmt = s.g.QTextCharFormat()
                choice = weekday if day < 6 else weekend
                colors = (
                    ["black", "blue", "green"] if day < 6 else ["red", "blue", "black"]
                )
                fmt.setForeground(
                    s.g.QBrush(s.g.QColor(colors[int(S.value(choice, "currentIndex"))]))
                )
                calendar.setWeekdayTextFormat(day, fmt)
            fmt = s.g.QTextCharFormat()
            fmt.setForeground(
                s.g.QBrush(
                    s.g.QColor(
                        ["black", "green", "blue"][int(S.value(header, "currentIndex"))]
                    )
                )
            )
            calendar.setHeaderTextFormat(fmt)
            for date in old:
                calendar.setDateTextFormat(date, s.g.QTextCharFormat())
            old.clear()
            if bool(S.value(special, "checked")):
                year = int(S.value(calendar, "yearShown"))
                month = int(S.value(calendar, "monthShown"))
                old.extend(
                    [
                        s.c.QDate(year, month, first_friday(year, month)),
                        s.c.QDate(year, 1, 1),
                    ]
                )
                for date in old:
                    mark = s.g.QTextCharFormat()
                    mark.setBackground(s.g.QBrush(s.g.QColor("#e6cb7a")))
                    calendar.setDateTextFormat(date, mark)
                s.state["first_friday"] = first_friday(year, month)

        for obj in [weekday, weekend, header]:
            s.link(obj, "currentIndexChanged(int)", formats)
        s.link(special, "toggled(bool)", formats)
        s.link(calendar, "currentPageChanged(int,int)", formats)
        return s.h
