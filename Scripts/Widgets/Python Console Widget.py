# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/5125860585e98b3a.md
# this_file: Scripts/Widgets/Python Console Widget.py

"""Show python console widget using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


def build(qt):
    history = []
    cursor = [0]

    class Entry(qt.QtGui.QLineEdit):
        def keyPressEvent(self, event):
            if event.key() in [qt.QtCore.Qt.Key_Up, qt.QtCore.Qt.Key_Down]:
                delta = -1 if event.key() == qt.QtCore.Qt.Key_Up else 1
                cursor[0] = max(0, min(len(history), cursor[0] + delta))
                self.setText(history[cursor[0]] if cursor[0] < len(history) else "")
            else:
                qt.QtGui.QLineEdit.keyPressEvent(self, event)

    with S.Session(qt, "Expression entry") as s:
        s.vertical()
        entry = s.keep("entry", Entry(s.window))
        s.add(entry)
        namespace = {"app": s.g.QApplication.instance(), "QtCore": s.c, "QtGui": s.g}
        s.state.update(history=[], result=None, error="")

        def evaluate(*args):
            expression = str(S.value(entry, "text"))
            try:
                result = eval(
                    compile(expression, "<example expression>", "eval"), namespace
                )
            except Exception as error:  # noqa: BLE001 - explicit expressions may raise any user exception.
                s.state["error"] = type(error).__name__ + ": " + str(error)
                return
            history.append(expression)
            cursor[0] = len(history)
            s.state.update(history=list(history), result=repr(result), error="")

        s.link(entry, "returnPressed()", evaluate)
        s.keep("evaluate", evaluate)
        return s.h


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_pythonconsolewidget-5125860585e98b3a', 'Python Console Widget')


if __name__ == "__main__":
    main()
