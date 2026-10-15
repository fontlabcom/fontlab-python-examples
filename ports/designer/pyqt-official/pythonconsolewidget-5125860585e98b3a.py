# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/5125860585e98b3a.md
# this_file: ports/designer/pyqt-official/pythonconsolewidget-5125860585e98b3a.py

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
