# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c56cf1699b07b350.md
# this_file: ports/richtext/pyqt-official/calendar-c56cf1699b07b350.py
"""Independent FontLab example with an explicitly owned lifetime."""

from contextlib import contextmanager

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    item = getattr(obj, name)
    return item() if callable(item) else item


@contextmanager
def owned(qt, title):
    state = {"closing": False}

    class Window(qt.QtGui.QWidget):
        def closeEvent(self, event):
            if not state["closing"]:
                handle.close()
            event.accept()

    window = Window()
    handle = ExampleHandle(window, dict)
    handle.cleanup.append(lambda: state.update(closing=True))
    try:
        window.setWindowTitle(title)
        window.setAttribute(qt.QtCore.Qt.WA_QuitOnClose, False)
        window.resize(760, 540)
        layout = qt.QtGui.QVBoxLayout(window)
        handle.controls["layout"] = layout
        yield handle, layout
    except BaseException:
        handle.close()
        raise


def wire(handle, obj, signature, callback):
    def receive(*args):
        if not handle.owner.closed:
            callback(*args)

    handle.connect_old(obj, signature, receive)
    return receive


import calendar
import datetime


def build(qt):
    gui = qt.QtGui
    with owned(qt, "Calendar") as (handle, layout):
        today = datetime.date.today()
        month = gui.QComboBox(handle.widget)
        month.addItems(list(calendar.month_name)[1:])
        month.setCurrentIndex(today.month - 1)
        year = gui.QSpinBox(handle.widget)
        year.setRange(1, 9999)
        year.setValue(today.year)
        size = gui.QSpinBox(handle.widget)
        size.setRange(1, 64)
        size.setValue(12)
        editor = gui.QTextEdit(handle.widget)
        editor.setReadOnly(True)
        for item in (month, year, size, editor):
            layout.addWidget(item)
        state = {}

        def generate(*args):
            y, m, points = (
                int(value(year, "value")),
                int(value(month, "currentIndex")) + 1,
                int(value(size, "value")),
            )
            weeks = calendar.monthcalendar(y, m)
            document = value(editor, "document")
            document.clear()
            cursor = gui.QTextCursor(document)
            form = gui.QTextCharFormat()
            form.setFontPointSize(points)
            cursor.setCharFormat(form)
            table = cursor.insertTable(len(weeks) + 1, 7)
            for col, name in enumerate(calendar.day_abbr):
                table.cellAt(0, col).firstCursorPosition().insertText(name)
            for row, week in enumerate(weeks, 1):
                for col, day in enumerate(week):
                    if day:
                        cell = table.cellAt(row, col).firstCursorPosition()
                        selected = gui.QTextCharFormat(form)
                        if (y, m, day) == (today.year, today.month, today.day):
                            selected.setBackground(gui.QBrush(gui.QColor("#ffe3a1")))
                        cell.insertText(str(day), selected)
            title = f"{calendar.month_name[m]} {y}"
            handle.widget.setWindowTitle(title)
            state.update(year=y, month=m, font_size=points, weeks=weeks, title=title)

        wire(handle, month, "currentIndexChanged(int)", generate)
        wire(handle, year, "valueChanged(int)", generate)
        wire(handle, size, "valueChanged(int)", generate)
        handle.controls.update(month=month, year=year, size=size, editor=editor)
        handle.inspect_ui = lambda: dict(state)
        generate()
        return handle
