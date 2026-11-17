# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/3040b9f6b267a196.md
# this_file: Scripts/Widgets/Digital Clock.py

"""Show digital clock using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S

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


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_digitalclock-3040b9f6b267a196', 'Digital Clock')


if __name__ == "__main__":
    main()
