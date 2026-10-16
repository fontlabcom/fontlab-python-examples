# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/428c50abcef7adfe.md
# this_file: ports/richtext/pyqt-official/syntaxhighlighter-428c50abcef7adfe.py

from contextlib import contextmanager
from pathlib import Path

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


def menu(qt, handle, layout, entries):
    bar = qt.QtGui.QMenuBar(handle.widget)
    layout.addWidget(bar)
    for title, actions in entries:
        group = bar.addMenu(title)
        for label, callback in actions:
            action = qt.QtGui.QAction(label, handle.widget)
            group.addAction(action)
            wire(handle, action, "triggered()", lambda *args, call=callback: call())
    return bar


def choose_file(qt, handle, save, callback, directory=""):
    dialog = qt.QtGui.QFileDialog(handle.widget)
    from fontlabapp.widgets import OwnedWidget

    owner = OwnedWidget(dialog, dialog)
    handle.alerts.append(owner)
    dialog.setOption(qt.QtGui.QFileDialog.DontUseNativeDialog, True)
    dialog.setDirectory(str(directory))
    dialog.setAcceptMode(
        qt.QtGui.QFileDialog.AcceptSave if save else qt.QtGui.QFileDialog.AcceptOpen
    )

    def selected(*args):
        files = list(dialog.selectedFiles())
        if files:
            callback(str(files[0]))

    wire(handle, dialog, "accepted()", selected)
    dialog.open()
    return dialog


import re


def spans(text, inside=False):
    """Return lexical spans and the continuation state of a block comment."""
    result = []
    expression = re.compile(
        r'/\*|//[^\n]*|"(?:\\.|[^"\\])*"|\b(?:class|struct|int|void|if|else|return|const|public|auto|for|while)\b|\b[A-Z]\w*\b|\b\w+(?=\s*\()'
    )
    position = 0
    while position < len(text):
        if inside:
            end = text.find("*/", position)
            stop = len(text) if end < 0 else end + 2
            result.append((position, stop - position, "comment"))
            position, inside = stop, end < 0
            if inside:
                break
            continue
        match = expression.search(text, position)
        if match is None:
            break
        token = match.group()
        if token == "/*":
            position, inside = match.start(), True
            continue
        kind = (
            "comment"
            if token.startswith("//")
            else "string"
            if token.startswith('"')
            else "keyword"
            if token
            in {
                "class",
                "struct",
                "int",
                "void",
                "if",
                "else",
                "return",
                "const",
                "public",
                "auto",
                "for",
                "while",
            }
            else "class"
            if token[0].isupper()
            else "call"
        )
        result.append((match.start(), len(token), kind))
        position = match.end()
    return result, inside


def build(qt):
    gui = qt.QtGui
    with owned(qt, "Source colorizer") as (handle, layout):
        editor, status = gui.QTextEdit(handle.widget), gui.QLabel("", handle.widget)
        layout.addWidget(editor)
        layout.addWidget(status)
        formats = {}
        for kind, color in {
            "keyword": "#234cb3",
            "class": "#7944a5",
            "call": "#1c7968",
            "string": "#aa5314",
            "comment": "#71806e",
        }.items():
            form = gui.QTextCharFormat()
            form.setForeground(gui.QBrush(gui.QColor(color)))
            formats[kind] = form

        class Colorizer(gui.QSyntaxHighlighter):
            def highlightBlock(self, text):
                ranges, continued = spans(str(text), self.previousBlockState() == 1)
                for offset, length, kind in ranges:
                    self.setFormat(offset, length, formats[kind])
                self.setCurrentBlockState(1 if continued else 0)

        highlighter = Colorizer(value(editor, "document"))
        handle.cleanup.append(lambda: highlighter.setDocument(None))
        handle.controls["highlighter"] = highlighter

        def open_file(path):
            try:
                contents = Path(path).read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                status.setText(str(error))
                return
            editor.setPlainText(contents)
            status.setText(Path(path).name)

        menu(
            qt,
            handle,
            layout,
            [
                (
                    "File",
                    [
                        ("New", editor.clear),
                        ("Open", lambda: choose_file(qt, handle, False, open_file)),
                        ("Exit", handle.close),
                    ],
                ),
                (
                    "Help",
                    [
                        (
                            "About",
                            lambda: status.setText(
                                "Edit source; comments may cross lines."
                            ),
                        )
                    ],
                ),
            ],
        )
        editor.setPlainText(
            "class River {\npublic: int depth() { return 4; }\n};\n/* moving\nwater */\n"
        )
        handle.controls.update(editor=editor, status=status, open_file=open_file)
        handle.inspect_ui = lambda: {"text": str(editor.toPlainText())}
        return handle
