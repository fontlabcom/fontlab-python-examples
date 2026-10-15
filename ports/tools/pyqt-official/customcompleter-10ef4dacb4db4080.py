# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/10ef4dacb4db4080.md
# this_file: ports/tools/pyqt-official/customcompleter-10ef4dacb4db4080.py

from contextlib import contextmanager

from fontlab_python_examples.handle import ExampleHandle


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


VOCABULARY = sorted(
    (
        "anchor",
        "anchorage",
        "angle",
        "angular",
        "baseline",
        "bezier",
        "contour",
        "contrast",
        "curve",
        "curvature",
        "spacing",
        "spectrum",
    ),
    key=str.casefold,
)


def completion_suffix(word, prefix):
    """Return only the remaining characters of a case-insensitive completion."""
    return (
        word[len(prefix) :] if word.casefold().startswith(prefix.casefold()) else None
    )


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Word completion") as (handle, layout):
        state = {"prefix": "", "activation": None, "completer": None}

        class Editor(gui.QTextEdit):
            def keyPressEvent(self, event):
                popup = state["completer"].popup() if state["completer"] else None
                key, modifiers = event.key(), event.modifiers()
                if (
                    popup is not None
                    and popup.isVisible()
                    and key
                    in (
                        core.Qt.Key_Enter,
                        core.Qt.Key_Return,
                        core.Qt.Key_Escape,
                        core.Qt.Key_Tab,
                        core.Qt.Key_Backtab,
                    )
                ):
                    event.ignore()
                    return
                explicit = key == core.Qt.Key_E and bool(
                    modifiers & core.Qt.ControlModifier
                )
                if not explicit:
                    gui.QTextEdit.keyPressEvent(self, event)
                cursor = self.textCursor()
                cursor.select(gui.QTextCursor.WordUnderCursor)
                prefix = str(cursor.selectedText())
                state["prefix"] = prefix
                allowed = not (
                    modifiers
                    & (
                        core.Qt.ControlModifier
                        | core.Qt.AltModifier
                        | core.Qt.MetaModifier
                    )
                )
                typed = str(event.text())
                if not explicit and (
                    len(prefix) < 3
                    or not allowed
                    or not typed
                    or not typed[-1].isalpha()
                ):
                    if popup is not None:
                        popup.hide()
                    return
                state["completer"].setCompletionPrefix(prefix)
                state["completer"].complete(self.cursorRect())

        editor = Editor(handle.widget)
        layout.addWidget(editor)

        def insert(word):
            text = str(word)
            cursor = editor.textCursor()
            cursor.select(gui.QTextCursor.WordUnderCursor)
            prefix = str(cursor.selectedText())
            suffix = completion_suffix(text, prefix)
            if suffix is not None:
                cursor.clearSelection()
                cursor.movePosition(gui.QTextCursor.EndOfWord)
                cursor.insertText(suffix)
                editor.setTextCursor(cursor)

        def replace(completer):
            previous = state["completer"]
            if previous is not None:
                pair = state["activation"]
                previous.disconnect("activated(QString)", pair)
                handle.connections.remove((previous, "activated(QString)", pair))
                popup = previous.popup()
                if popup is not None:
                    popup.hide()
                previous.setWidget(None)
                previous.deleteLater()
            state["completer"] = completer
            completer.setWidget(editor)
            completer.setCaseSensitivity(core.Qt.CaseInsensitive)
            completer.setModelSorting(gui.QCompleter.CaseInsensitivelySortedModel)
            completer.setCompletionMode(gui.QCompleter.PopupCompletion)
            state["activation"] = wire(handle, completer, "activated(QString)", insert)
            handle.controls["completer"] = completer

        model = gui.QStringListModel(list(VOCABULARY), handle.widget)
        completer = gui.QCompleter(model, handle.widget)
        replace(completer)
        menu(
            qt,
            handle,
            layout,
            [
                ("File", [("New", editor.clear), ("Close", handle.close)]),
                (
                    "About",
                    [("Vocabulary", lambda: editor.setToolTip(", ".join(VOCABULARY)))],
                ),
            ],
        )
        handle.controls.update(
            editor=editor,
            insert_completion=insert,
            replace_completer=replace,
            model=model,
        )
        handle.inspect_ui = lambda: {
            "text": str(editor.toPlainText()),
            "prefix": state["prefix"],
            "vocabulary": list(VOCABULARY),
        }
        return handle
