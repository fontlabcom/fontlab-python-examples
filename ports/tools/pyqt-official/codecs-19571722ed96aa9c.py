# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/19571722ed96aa9c.md
# this_file: ports/tools/pyqt-official/codecs-19571722ed96aa9c.py

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


def raw_bytes(array):
    data = array.data() if hasattr(array, "data") else array
    return data.encode("latin1") if isinstance(data, str) else bytes(data)


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Encoding workbench") as (handle, layout):
        root = workspace(handle)
        (root / "unicode.txt").write_bytes(
            "A river reflects the moon. Ω\n".encode("utf-8")
        )
        (root / "western.txt").write_bytes(
            "Café beside the river.\n".encode("iso-8859-1")
        )
        editor, status = (
            gui.QTextEdit(handle.widget),
            gui.QLabel(str(root), handle.widget),
        )
        layout.addWidget(editor)
        layout.addWidget(status)
        names = [
            raw_bytes(core.QTextCodec.codecForMib(mib).name()).decode("ascii")
            for mib in core.QTextCodec.availableMibs()
        ]
        preferred = ["UTF-8", "UTF-16", "ISO-8859-1", "windows-1252"]
        names = sorted(
            set(names),
            key=lambda name: (
                next(
                    (i for i, p in enumerate(preferred) if p.lower() == name.lower()),
                    99,
                ),
                name.lower(),
            ),
        )

        def preview(path):
            try:
                data = Path(path).read_bytes()
            except OSError as error:
                status.setText(str(error))
                return
            dialog = gui.QDialog(handle.widget)
            from fontlabapp.widgets import OwnedWidget

            handle.alerts.append(OwnedWidget(dialog, dialog))
            box = gui.QVBoxLayout(dialog)
            selector = gui.QComboBox(dialog)
            selector.addItems(names)
            text = gui.QTextEdit(dialog)
            text.setReadOnly(True)
            box.addWidget(selector)
            box.addWidget(text)

            def decode(*args):
                codec = core.QTextCodec.codecForName(
                    str(value(selector, "currentText")).encode("ascii")
                )
                text.setPlainText(str(codec.toUnicode(core.QByteArray(data))))

            accept = gui.QPushButton("Use decoded text", dialog)
            cancel = gui.QPushButton("Cancel", dialog)
            box.addWidget(accept)
            box.addWidget(cancel)
            wire(handle, selector, "currentIndexChanged(int)", decode)
            wire(
                handle,
                accept,
                "clicked()",
                lambda *args: (editor.setPlainText(text.toPlainText()), dialog.hide()),
            )
            wire(handle, cancel, "clicked()", lambda *args: dialog.hide())
            handle.controls.update(
                preview=dialog, preview_text=text, preview_codec=selector
            )
            decode()
            dialog.open()

        def save(path, encoding):
            try:
                target = Path(path).resolve()
                if (
                    not target.is_relative_to(root.resolve())
                    or target == root.resolve()
                ):
                    raise ValueError("Save inside the displayed example directory")
                # Strict conversion reports unrepresentable characters before writing.
                data = str(editor.toPlainText()).encode(encoding)
                target.write_bytes(data)
                status.setText(f"Saved {target.name} using {encoding}")
            except (OSError, ValueError, LookupError) as error:
                status.setText(str(error))

        saves = [
            (
                name,
                lambda codec=name: choose_file(
                    qt, handle, True, lambda path: save(path, codec), root
                ),
            )
            for name in names
        ]
        menu(
            qt,
            handle,
            layout,
            [
                (
                    "File",
                    [
                        ("Open", lambda: choose_file(qt, handle, False, preview, root)),
                        *[("Save As " + name, action) for name, action in saves],
                        ("Exit", handle.close),
                    ],
                ),
                (
                    "Help",
                    [
                        (
                            "About",
                            lambda: status.setText(
                                "Preview bytes before choosing their encoding."
                            ),
                        )
                    ],
                ),
            ],
        )
        handle.controls.update(
            editor=editor, status=status, preview_file=preview, save_file=save
        )
        handle.inspect_ui = lambda: {
            "text": str(editor.toPlainText()),
            "encodings": names,
            "status": str(value(status, "text")),
        }
        return handle
