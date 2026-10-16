# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/9e41e71c41b116a8.md
# this_file: ports/tools/pyqt-official/settingseditor-9e41e71c41b116a8.py

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


def timer(qt, handle, interval, callback):
    item = qt.QtCore.QTimer(handle.widget)
    wire(handle, item, "timeout()", lambda *args: callback())
    handle.cleanup.append(item.stop)
    item.start(interval)
    return item


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


import plistlib
import shutil


def parse_scalar(text, kind, core):
    if kind == "bool":
        lowered = text.strip().lower()
        if lowered not in {"true", "false"}:
            raise ValueError("Use true or false")
        return lowered == "true"
    if kind == "int":
        return int(text)
    if kind == "float":
        return float(text)
    if kind == "bytes":
        return core.QByteArray(bytes.fromhex(text))
    if kind in {"QDate", "QTime", "QDateTime"}:
        result = getattr(core, kind).fromString(text, core.Qt.ISODate)
        if not result.isValid():
            raise ValueError("Use an ISO date or time")
        return result
    return text


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Temporary settings editor") as (handle, layout):
        root = workspace(handle)
        target = root / "working.ini"
        settings = core.QSettings(str(target), core.QSettings.IniFormat, handle.widget)
        settings.setFallbacksEnabled(False)
        for key, item in {
            "display/enabled": False,
            "display/size": 18,
            "display/ratio": 1.25,
            "identity/title": "River",
            "identity/tag": core.QByteArray(b"AB"),
            "time/day": core.QDate(2026, 10, 15),
            "time/clock": core.QTime(12, 30),
            "time/stamp": core.QDateTime(core.QDate(2026, 10, 15), core.QTime(12, 30)),
        }.items():
            settings.setValue(key, item)
        settings.sync()
        tree = gui.QTreeWidget(handle.widget)
        tree.setColumnCount(3)
        tree.setHeaderLabels(["Setting", "Type", "Value"])
        status = gui.QLabel(str(target), handle.widget)
        layout.addWidget(tree)
        layout.addWidget(status)
        state = {"refreshing": False, "editing": False, "types": {}}

        class ValueDelegate(gui.QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                if index.column() != 2:
                    return None
                kind = str(index.sibling(index.row(), 1).data(core.Qt.DisplayRole))
                if kind == "bool":
                    editor = gui.QComboBox(parent)
                    editor.addItems(["false", "true"])
                    return editor
                if kind == "int":
                    editor = gui.QSpinBox(parent)
                    editor.setRange(-2147483648, 2147483647)
                    return editor
                if kind == "float":
                    editor = gui.QDoubleSpinBox(parent)
                    editor.setRange(-1e12, 1e12)
                    editor.setDecimals(8)
                    return editor
                return gui.QLineEdit(parent)

            def setEditorData(self, editor, index):
                text = str(index.data(core.Qt.EditRole))
                if editor.inherits("QComboBox"):
                    editor.setCurrentIndex(1 if text.lower() == "true" else 0)
                elif editor.inherits("QSpinBox"):
                    editor.setValue(int(text))
                elif editor.inherits("QDoubleSpinBox"):
                    editor.setValue(float(text))
                else:
                    editor.setText(text)

            def setModelData(self, editor, model, index):
                if editor.inherits("QComboBox"):
                    text = str(value(editor, "currentText"))
                elif editor.inherits("QSpinBox") or editor.inherits("QDoubleSpinBox"):
                    text = str(value(editor, "value"))
                else:
                    text = str(value(editor, "text"))
                model.setData(index, text, core.Qt.EditRole)

        delegate = ValueDelegate(tree)
        tree.setItemDelegate(delegate)
        handle.controls["delegate"] = delegate

        def icon(color, group=False):
            image = gui.QPixmap(18, 18)
            image.fill(gui.QColor("white"))
            painter = gui.QPainter(image)
            try:
                painter.setBrush(gui.QBrush(gui.QColor(color)))
                painter.drawRect(2, 5 if group else 3, 14, 10)
                if group:
                    painter.drawRect(2, 3, 6, 3)
            finally:
                painter.end()
            return gui.QIcon(image)

        group_icon, key_icon = icon("#a9c4d2", True), icon("#d2b676")

        def kind_of(item):
            if isinstance(item, bool):
                return "bool"
            if isinstance(item, int):
                return "int"
            if isinstance(item, float):
                return "float"
            for name in ("QByteArray", "QDate", "QTime", "QDateTime"):
                if isinstance(item, getattr(core, name)):
                    return "bytes" if name == "QByteArray" else name
            return "str"

        def show(item, kind):
            if kind == "bool":
                return "true" if item else "false"
            if kind == "bytes":
                return bytes(item.data()).hex()
            if kind.startswith("Q"):
                return str(item.toString(core.Qt.ISODate))
            return str(item)

        def refresh(*args):
            if state["editing"]:
                return
            state["refreshing"] = True
            tree.blockSignals(True)
            try:
                settings.sync()
                tree.clear()
                state["types"].clear()
                parents = {}
                for key in sorted(str(k) for k in settings.allKeys()):
                    item_value = settings.value(key)
                    kind = kind_of(item_value)
                    parts = key.split("/")
                    parent = tree
                    path = ""
                    for part in parts[:-1]:
                        path += "/" + part
                        if path not in parents:
                            branch = gui.QTreeWidgetItem(parent, [part, "", ""])
                            branch.setIcon(0, group_icon)
                            parents[path] = branch
                        parent = parents[path]
                    item = gui.QTreeWidgetItem(
                        parent, [parts[-1], kind, show(item_value, kind)]
                    )
                    item.setIcon(0, key_icon)
                    item.setData(0, core.Qt.UserRole, key)
                    item.setFlags(item.flags() | core.Qt.ItemIsEditable)
                    state["types"][key] = kind
                tree.expandAll()
            finally:
                tree.blockSignals(False)
                state["refreshing"] = False

        def changed(item, column):
            if state["refreshing"] or column != 2:
                return
            key = str(item.data(0, core.Qt.UserRole))
            try:
                converted = parse_scalar(str(item.text(2)), state["types"][key], core)
                settings.setValue(key, converted)
                settings.sync()
                status.setText("Saved " + key + " in the temporary copy")
            except (ValueError, TypeError) as error:
                status.setText(str(error))
                refresh()

        def import_file(path):
            try:
                source = Path(path)
                if source.suffix.lower() == ".plist":
                    data = plistlib.loads(source.read_bytes())
                    if not isinstance(data, dict):
                        raise ValueError("Property list must contain a dictionary")
                    settings.clear()

                    def add(prefix, mapping):
                        for key, item in mapping.items():
                            name = prefix + str(key)
                            if isinstance(item, dict):
                                add(name + "/", item)
                            else:
                                settings.setValue(name, item)

                    add("", data)
                else:
                    # Copy bytes to an owned staging path, then read through QSettings.
                    staged = root / "import.ini"
                    shutil.copyfile(source, staged)
                    other = core.QSettings(
                        str(staged), core.QSettings.IniFormat, handle.widget
                    )
                    try:
                        if other.status() in (
                            core.QSettings.AccessError,
                            core.QSettings.FormatError,
                        ):
                            raise ValueError("Cannot read this settings file")
                        copied = {
                            str(key): other.value(str(key)) for key in other.allKeys()
                        }
                        settings.clear()
                        for key, item in copied.items():
                            settings.setValue(key, item)
                    finally:
                        other.deleteLater()
                settings.sync()
                refresh()
            except (OSError, ValueError, plistlib.InvalidFileException) as error:
                status.setText(str(error))

        def select_application():
            from fontlabapp.widgets import OwnedWidget

            dialog = gui.QDialog(handle.widget)
            handle.alerts.append(OwnedWidget(dialog, dialog))
            box = gui.QVBoxLayout(dialog)
            organization = gui.QLineEdit("ExampleWorkshop", dialog)
            application = gui.QLineEdit("DrawingNotes", dialog)
            preview = gui.QLabel(
                "Select a source; only its temporary copy will be edited.", dialog
            )
            for text, control in (
                ("Organization", organization),
                ("Application", application),
            ):
                box.addWidget(gui.QLabel(text, dialog))
                box.addWidget(control)
            box.addWidget(preview)

            def source():
                original = core.QSettings(
                    str(value(organization, "text")),
                    str(value(application, "text")),
                    handle.widget,
                )
                original.setFallbacksEnabled(False)
                return original

            def show_location(*args):
                original = source()
                try:
                    preview.setText(
                        str(value(original, "fileName")) + " → " + str(target)
                    )
                finally:
                    original.deleteLater()

            def use_copy(*args):
                original = source()
                try:
                    copied = {
                        str(key): original.value(str(key)) for key in original.allKeys()
                    }
                    settings.clear()
                    for key, item in copied.items():
                        settings.setValue(key, item)
                    settings.sync()
                    refresh()
                    dialog.hide()
                finally:
                    original.deleteLater()

            for text, action in (
                ("Preview locations", show_location),
                ("Edit temporary copy", use_copy),
                ("Cancel", lambda *args: dialog.hide()),
            ):
                control = gui.QPushButton(text, dialog)
                box.addWidget(control)
                wire(handle, control, "clicked()", action)
            handle.controls["selection"] = dialog
            dialog.open()

        menu(
            qt,
            handle,
            layout,
            [
                (
                    "File",
                    [
                        ("Application settings", select_application),
                        (
                            "Import INI / plist",
                            lambda: choose_file(qt, handle, False, import_file, root),
                        ),
                        ("Close", handle.close),
                    ],
                ),
                ("Options", [("Refresh", refresh)]),
                (
                    "Help",
                    [
                        (
                            "Storage",
                            lambda: status.setText(
                                "Working storage: "
                                + str(target)
                                + "; registry unavailable; fallbacks disabled"
                            ),
                        )
                    ],
                ),
            ],
        )
        automatic = gui.QCheckBox("Automatic refresh", handle.widget)
        layout.addWidget(automatic)
        fallbacks = gui.QCheckBox(
            "Fallbacks (disabled; registry unavailable)", handle.widget
        )
        fallbacks.setChecked(False)
        fallbacks.setEnabled(False)
        layout.addWidget(fallbacks)

        def auto_refresh():
            if (
                value(automatic, "checked")
                and value(tree, "state") != gui.QAbstractItemView.EditingState
            ):
                refresh()

        ticker = timer(qt, handle, 1000, auto_refresh)
        wire(handle, tree, "itemChanged(QTreeWidgetItem*,int)", changed)
        handle.controls.update(
            tree=tree,
            settings=settings,
            status=status,
            refresh=refresh,
            import_file=import_file,
            timer=ticker,
        )
        handle.inspect_ui = lambda: {
            "keys": sorted(state["types"]),
            "storage": str(target),
            "fallbacks": False,
        }
        refresh()
        return handle
