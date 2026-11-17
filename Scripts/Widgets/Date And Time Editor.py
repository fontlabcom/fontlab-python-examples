# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/7ba49e67588b1329.md
# this_file: Scripts/Widgets/Date And Time Editor.py

"""Show date and time editor using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


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


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_datetimeedit-7ba49e67588b1329', 'Date And Time Editor')


if __name__ == "__main__":
    main()
