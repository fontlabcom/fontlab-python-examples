# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b34b2f696a977e74.md
# this_file: ports/richtext/pyqt-official/textedit-b34b2f696a977e74.py

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    item = getattr(obj, name)
    return item() if callable(item) else item


@contextmanager
def owned(qt, title):
    state = {"closing": False}

    class Window(qt.QtGui.QWidget):
        def closeEvent(self, event):
            if not state["closing"] and "request_close" in handle.controls:
                handle.controls["request_close"]()
                event.ignore()
                return
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


def workspace(handle):
    folder = TemporaryDirectory(prefix="fontlab-example-")
    handle.after_close.append(folder.cleanup)
    handle.controls["directory"] = folder.name
    return Path(folder.name)


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


import hashlib
import re
import shutil


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Rich editor") as (handle, layout):
        root = workspace(handle)
        cache = root / "images"
        cache.mkdir()
        demonstration = root / "demonstration.html"
        demonstration.write_text(
            "<h2>Notes beside the river</h2><p>A fresh page for <b>clear ideas</b>.</p>",
            encoding="utf-8",
        )
        editor, status = (
            gui.QTextEdit(handle.widget),
            gui.QLabel(str(root), handle.widget),
        )
        layout.addWidget(editor)
        layout.addWidget(status)
        document = value(editor, "document")
        state = {"filename": "", "pending": None}
        from fontlabapp.widgets import OwnedWidget

        def update_title(*args):
            modified = bool(value(document, "modified"))
            handle.widget.setWindowTitle(
                (Path(state["filename"]).name if state["filename"] else "Untitled")
                + (" *" if modified else "")
                + " — Rich editor"
            )

        def owned_target(path):
            target = Path(path).resolve()
            if (
                not target.is_relative_to(root.resolve())
                or target == root.resolve()
                or target == demonstration.resolve()
            ):
                raise ValueError(
                    "Choose a new output within the displayed example directory"
                )
            return target

        def save(path, after=None):
            try:
                target = owned_target(path)
                content = (
                    str(editor.toHtml())
                    if target.suffix.lower() in {".html", ".htm"}
                    else str(editor.toPlainText())
                )
                target.write_text(content, encoding="utf-8")
            except (OSError, ValueError) as error:
                status.setText(str(error))
                return False
            state["filename"] = str(target)
            document.setModified(False)
            update_title()
            status.setText("Saved " + target.name)
            if after is not None:
                after()
            return True

        def save_as(after=None):
            choose_file(qt, handle, True, lambda path: save(path, after), root)

        def guard(action):
            if not bool(value(document, "modified")):
                action()
                return
            if state["pending"] is not None:
                state["pending"].show()
                return
            box = gui.QMessageBox(handle.widget)
            box.setText("Save changes before continuing?")
            box.setStandardButtons(
                gui.QMessageBox.Save | gui.QMessageBox.Discard | gui.QMessageBox.Cancel
            )
            handle.alerts.append(OwnedWidget(box, box))
            state["pending"] = box

            def finish(result):
                state["pending"] = None
                if result == gui.QMessageBox.Discard:
                    action()
                elif result == gui.QMessageBox.Save:
                    if state["filename"]:
                        save(state["filename"], action)
                    else:
                        save_as(action)

            wire(handle, box, "finished(int)", finish)
            box.open()

        def clear():
            editor.clear()
            state["filename"] = ""
            document.setModified(False)
            update_title()

        def load(path):
            try:
                source = Path(path).resolve()
                text = source.read_text(encoding="utf-8")
                if source.suffix.lower() in {".html", ".htm"}:

                    def rewrite(match):
                        raw = match.group(2)
                        image = (source.parent / raw).resolve()
                        if (
                            ":" in raw
                            or not image.is_relative_to(source.parent)
                            or not image.is_file()
                        ):
                            return match.group(1) + '""'
                        target = cache / (
                            hashlib.sha256(image.read_bytes()).hexdigest()
                            + image.suffix
                        )
                        shutil.copyfile(image, target)
                        return (
                            match.group(1)
                            + '"'
                            + core.QUrl.fromLocalFile(str(target)).toString()
                            + '"'
                        )

                    text = re.sub(
                        r'(<img\b[^>]*?\bsrc\s*=\s*)["\x27]([^"\x27]*)["\x27]',
                        rewrite,
                        text,
                        flags=re.I,
                    )
                    editor.setHtml(text)
                else:
                    editor.setPlainText(text)
                # Imported documents always save to a new owned path.
                state["filename"] = ""
                document.setModified(False)
                update_title()
                status.setText(
                    "Opened " + source.name + "; save a copy in " + str(root)
                )
            except (OSError, UnicodeError) as error:
                status.setText(str(error))

        def merge(form):
            cursor = editor.textCursor()
            if not cursor.hasSelection():
                cursor.select(gui.QTextCursor.WordUnderCursor)
            cursor.mergeCharFormat(form)
            editor.mergeCurrentCharFormat(form)

        toolbar = gui.QToolBar(handle.widget)
        layout.addWidget(toolbar)

        def format_action(label, setter, on, off):
            action = gui.QAction(label, handle.widget)
            action.setCheckable(True)
            toolbar.addAction(action)

            def toggle(checked):
                form = gui.QTextCharFormat()
                getattr(form, setter)(on if checked else off)
                merge(form)

            wire(handle, action, "toggled(bool)", toggle)
            handle.controls[label] = action
            return action

        bold = format_action("Bold", "setFontWeight", gui.QFont.Bold, gui.QFont.Normal)
        italic = format_action("Italic", "setFontItalic", True, False)
        underline = format_action("Underline", "setFontUnderline", True, False)
        family = gui.QFontComboBox(handle.widget)
        size = gui.QComboBox(handle.widget)
        size.setEditable(True)
        size.addItems(["8", "10", "12", "14", "18", "24", "36", "48", "64"])
        toolbar.addWidget(family)
        toolbar.addWidget(size)

        def family_changed(font):
            form = gui.QTextCharFormat()
            form.setFontFamily(str(value(font, "family")))
            merge(form)

        def size_changed(*args):
            try:
                points = float(value(size, "currentText"))
                if not 1 <= points <= 200:
                    raise ValueError("Font size must be between 1 and 200")
                form = gui.QTextCharFormat()
                form.setFontPointSize(points)
                merge(form)
            except ValueError as error:
                status.setText(str(error))

        wire(handle, family, "currentFontChanged(QFont)", family_changed)
        wire(handle, size, "activated(QString)", size_changed)

        def color():
            dialog = gui.QColorDialog(handle.widget)
            dialog.setOption(gui.QColorDialog.DontUseNativeDialog, True)
            handle.alerts.append(OwnedWidget(dialog, dialog))

            def accept(*args):
                form = gui.QTextCharFormat()
                form.setForeground(gui.QBrush(value(dialog, "selectedColor")))
                merge(form)

            wire(handle, dialog, "accepted()", accept)
            dialog.open()

        action = gui.QAction("Color", handle.widget)
        toolbar.addAction(action)
        wire(handle, action, "triggered()", lambda *args: color())
        alignments = [
            ("Left", core.Qt.AlignLeft),
            ("Center", core.Qt.AlignHCenter),
            ("Right", core.Qt.AlignRight),
            ("Justify", core.Qt.AlignJustify),
        ]
        for label, alignment in alignments:
            action = gui.QAction(label, handle.widget)
            toolbar.addAction(action)
            wire(
                handle,
                action,
                "triggered()",
                lambda *args, a=alignment: editor.setAlignment(a),
            )
        styles = gui.QComboBox(handle.widget)
        styles.addItems(
            [
                "Paragraph",
                "Disc",
                "Circle",
                "Square",
                "Decimal",
                "Lower alpha",
                "Upper alpha",
                "Lower roman",
                "Upper roman",
            ]
        )
        toolbar.addWidget(styles)

        def style_changed(index):
            cursor = editor.textCursor()
            cursor.beginEditBlock()
            try:
                if index:
                    names = [
                        "ListDisc",
                        "ListCircle",
                        "ListSquare",
                        "ListDecimal",
                        "ListLowerAlpha",
                        "ListUpperAlpha",
                        "ListLowerRoman",
                        "ListUpperRoman",
                    ]
                    form = gui.QTextListFormat()
                    form.setStyle(getattr(gui.QTextListFormat, names[index - 1]))
                    form.setIndent(1)
                    cursor.createList(form)
                else:
                    block = cursor.blockFormat()
                    block.setObjectIndex(-1)
                    cursor.setBlockFormat(block)
            finally:
                cursor.endEditBlock()

        wire(handle, styles, "currentIndexChanged(int)", style_changed)
        printer = gui.QPrinter(gui.QPrinter.HighResolution)
        printer.setOutputFormat(gui.QPrinter.PdfFormat)
        printer.setOutputFileName(str(root / "printed.pdf"))

        def print_document():
            path = str(value(printer, "outputFileName"))
            if path:
                owned_target(path)
            document.print(printer)

        def print_dialog():
            dialog = gui.QPrintDialog(printer, handle.widget)
            handle.alerts.append(OwnedWidget(dialog, dialog))
            wire(handle, dialog, "accepted()", lambda *args: print_document())
            dialog.open()

        def preview():
            dialog = gui.QPrintPreviewDialog(printer, handle.widget)
            handle.alerts.append(OwnedWidget(dialog, dialog))
            wire(
                handle,
                dialog,
                "paintRequested(QPrinter*)",
                lambda output: document.print(output),
            )
            dialog.open()

        def pdf(path):
            try:
                target = owned_target(path)
                output = gui.QPrinter(gui.QPrinter.HighResolution)
                output.setOutputFormat(gui.QPrinter.PdfFormat)
                output.setOutputFileName(str(target))
                document.print(output)
                status.setText("Exported " + target.name)
            except (OSError, ValueError) as error:
                status.setText(str(error))

        menu(
            qt,
            handle,
            layout,
            [
                (
                    "File",
                    [
                        ("New", lambda: guard(clear)),
                        (
                            "Open",
                            lambda: guard(
                                lambda: choose_file(qt, handle, False, load, root)
                            ),
                        ),
                        (
                            "Save",
                            lambda: (
                                save(state["filename"])
                                if state["filename"]
                                else save_as()
                            ),
                        ),
                        ("Save As", save_as),
                        ("Print", print_dialog),
                        ("Preview", preview),
                        (
                            "Export PDF",
                            lambda: choose_file(qt, handle, True, pdf, root),
                        ),
                        ("Close", lambda: guard(handle.close)),
                    ],
                ),
                (
                    "Edit",
                    [
                        (name, getattr(editor, name.lower()))
                        for name in ("Undo", "Redo", "Cut", "Copy", "Paste")
                    ],
                ),
                ("Format", [("Text color", color)]),
                (
                    "Help",
                    [
                        (
                            "About",
                            lambda: status.setText(
                                "Rich text with owned output copies in " + str(root)
                            ),
                        )
                    ],
                ),
            ],
        )
        wire(handle, document, "modificationChanged(bool)", update_title)

        def sync_format(form):
            for action, checked in (
                (bold, value(form, "fontWeight") == gui.QFont.Bold),
                (italic, bool(value(form, "fontItalic"))),
                (underline, bool(value(form, "fontUnderline"))),
            ):
                action.blockSignals(True)
                action.setChecked(checked)
                action.blockSignals(False)

        wire(handle, editor, "currentCharFormatChanged(QTextCharFormat)", sync_format)
        handle.controls.update(
            editor=editor,
            status=status,
            family=family,
            size=size,
            styles=styles,
            printer=printer,
            open_file=load,
            save_file=save,
            export_pdf=pdf,
            guard=guard,
            request_close=lambda: guard(handle.close),
        )
        handle.inspect_ui = lambda: {
            "text": str(editor.toPlainText()),
            "modified": bool(value(document, "modified")),
            "filename": state["filename"],
        }
        load(demonstration)
        return handle
