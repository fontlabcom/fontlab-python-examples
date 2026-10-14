# this_file: fontlab_python_examples/editor.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples numbered text editors 07/09/10.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json.
"""Original editor actions scoped to one owned window and UTF-8 files."""

from pathlib import Path
from typing import Any

from .handle import ExampleHandle


def apply_style(widget: Any, style: Any) -> None:
    """QWidget.setStyle does not propagate; visit only this owned subtree."""
    if widget.inherits("QWidget"):
        widget.setStyle(style)
    for child in widget.children():
        apply_style(child, style)


def selected_path(result: Any) -> str:
    """PythonQt returns a filename; tuple boundaries retain their first value."""
    return str(result[0] if isinstance(result, (tuple, list)) else result)


def build_editor(qt: Any, text: Any, icon: Path) -> ExampleHandle:
    gui = qt.QtGui
    state = {"file_path": None, "error": ""}
    closing = [False]

    class MainWindow(gui.QMainWindow):
        def closeEvent(self, event: Any) -> None:
            if closing[0] or not text.document().isModified():
                event.accept()
                return
            from fontlabapp.widgets import OwnedWidget

            box = gui.QMessageBox(self)
            box.setText("You have unsaved changes. Save before closing?")
            box.setStandardButtons(
                gui.QMessageBox.Save | gui.QMessageBox.Discard | gui.QMessageBox.Cancel
            )
            box.setWindowModality(qt.QtCore.Qt.WindowModal)
            handle.alerts.append(OwnedWidget(box, box))

            def answered(button: Any) -> None:
                choice = box.standardButton(button)
                if choice == gui.QMessageBox.Save:
                    save()
                    if text.document().isModified():
                        return
                elif choice != gui.QMessageBox.Discard:
                    return
                closing[0] = True
                self.close()
                closing[0] = False

            handle.connect(box.buttonClicked, answered)
            handle.callbacks.append(answered)
            box.open()
            event.ignore()

    window = MainWindow()
    window.setWindowTitle("Text Editor")
    window.setCentralWidget(text)
    handle = ExampleHandle(
        window,
        lambda: {
            "text": str(text.toPlainText()),
            "modified": bool(text.document().isModified()),
            **state,
        },
    )
    handle.cleanup.append(lambda: closing.__setitem__(0, True))

    def open_file() -> None:
        path = selected_path(gui.QFileDialog.getOpenFileName(window, "Open"))
        if path:
            try:
                content = Path(path).read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                state["error"] = str(error)
                return
            text.setPlainText(content)
            state.update(file_path=path, error="")

    def save() -> None:
        if state["file_path"] is None:
            save_as()
            return
        try:
            Path(state["file_path"]).write_text(
                str(text.toPlainText()), encoding="utf-8"
            )
        except (OSError, UnicodeError) as error:
            state["error"] = str(error)
            return
        state["error"] = ""
        text.document().setModified(False)

    def save_as() -> None:
        path = selected_path(gui.QFileDialog.getSaveFileName(window, "Save As"))
        if path:
            state["file_path"] = path
            save()

    def about() -> None:
        from fontlabapp.widgets import OwnedWidget

        box = gui.QMessageBox(window)
        box.setWindowTitle("About Text Editor")
        box.setText(
            f'<center><h1>Text Editor</h1>&#8291;<img src="{icon.as_uri()}"></center><p>Version 31.4.159.265358<br/>Copyright &copy; Company Inc.</p>'
        )
        box.setWindowModality(qt.QtCore.Qt.WindowModal)
        handle.alerts.append(OwnedWidget(box, box))
        box.open()

    file_menu = window.menuBar().addMenu("&File")
    help_menu = window.menuBar().addMenu("&Help")
    for label, callback, shortcut, menu in (
        ("&Open", open_file, gui.QKeySequence.Open, file_menu),
        ("&Save", save, gui.QKeySequence.Save, file_menu),
        ("Save &As...", save_as, None, file_menu),
        ("&Close", window.close, None, file_menu),
        ("&About", about, None, help_menu),
    ):
        action = gui.QAction(label, window)
        if shortcut is not None:
            action.setShortcut(gui.QKeySequence(shortcut))
        handle.connect(action.triggered, callback)
        menu.addAction(action)
        handle.callbacks.append(callback)

    def release_widgets() -> None:
        nonlocal text, window
        text = window = None

    handle.release.append(release_widgets)
    return handle
