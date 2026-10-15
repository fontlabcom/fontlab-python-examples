# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/626fd0acec74fd91.md
# this_file: ports/tools/pyqt-official/regexp-626fd0acec74fd91.py
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


import json


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Pattern laboratory") as (handle, layout):
        fields = {}
        for name, text in (("pattern", "(s\\w+)"), ("input", "small stones")):
            edit = gui.QComboBox(handle.widget)
            edit.setEditable(True)
            edit.addItem(text)
            layout.addWidget(edit)
            fields[name] = edit
        syntax = gui.QComboBox(handle.widget)
        syntax.addItems(
            ["Regular expression", "Regular expression 2", "Wildcard", "Fixed string"]
        )
        layout.addWidget(syntax)
        case = gui.QCheckBox("Case sensitive", handle.widget)
        minimal = gui.QCheckBox("Minimal match", handle.widget)
        layout.addWidget(case)
        layout.addWidget(minimal)
        output = gui.QTextEdit(handle.widget)
        output.setReadOnly(True)
        layout.addWidget(output)
        state = {}

        def refresh(*args):
            pattern = str(value(fields["pattern"], "currentText"))
            text = str(value(fields["input"], "currentText"))
            modes = [
                core.QRegExp.RegExp,
                core.QRegExp.RegExp2,
                core.QRegExp.Wildcard,
                core.QRegExp.FixedString,
            ]
            expression = core.QRegExp(pattern)
            expression.setPatternSyntax(modes[int(value(syntax, "currentIndex"))])
            expression.setCaseSensitivity(
                core.Qt.CaseSensitive
                if value(case, "checked")
                else core.Qt.CaseInsensitive
            )
            expression.setMinimal(bool(value(minimal, "checked")))
            position = expression.indexIn(text)
            captures = (
                [expression.cap(i) for i in range(expression.captureCount() + 1)]
                if position >= 0
                else []
            )
            state.update(
                pattern=pattern,
                escaped=json.dumps(pattern),
                position=position,
                length=expression.matchedLength() if position >= 0 else -1,
                captures=captures,
            )
            output.setPlainText(json.dumps(state, ensure_ascii=False, indent=2))

        for edit in fields.values():
            wire(handle, edit, "editTextChanged(QString)", refresh)
        wire(handle, syntax, "currentIndexChanged(int)", refresh)
        for item in (case, minimal):
            wire(handle, item, "toggled(bool)", refresh)
        handle.controls.update(
            fields,
            syntax=syntax,
            case=case,
            minimal=minimal,
            output=output,
            refresh=refresh,
        )
        handle.inspect_ui = lambda: dict(state)
        refresh()
        return handle
