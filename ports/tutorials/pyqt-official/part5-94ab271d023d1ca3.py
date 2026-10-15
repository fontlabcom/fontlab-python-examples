# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/94ab271d023d1ca3.md
# this_file: ports/tutorials/pyqt-official/part5-94ab271d023d1ca3.py
TITLE = "Address collection — stage 5"
MAIN = False
STAGE = 5

from pathlib import Path
from tempfile import TemporaryDirectory

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    result = getattr(obj, name)
    return result() if callable(result) else result


class Session:
    """One example lifetime; Python state stays off native wrappers."""

    def __init__(self, qt, title, main=False):
        self.qt, self.gui, self.core = qt, qt.QtGui, qt.QtCore
        self.state = {}
        self.pending = []
        self.temporary = None
        self.closing = False
        self.before_close = None
        session = self
        base = self.gui.QMainWindow if main else self.gui.QWidget

        class Window(base):
            def closeEvent(self, event):
                if session.state.get("dragging", False):
                    event.ignore()
                    return
                if session.closing:
                    event.accept()
                elif session.before_close:
                    event.ignore()
                    session.before_close()
                else:
                    event.ignore()
                    session.handle.close()

        self.window = Window()
        self.window.setWindowTitle(title)
        self.window.setAttribute(self.core.Qt.WA_QuitOnClose, False)
        self.window.setAttribute(self.core.Qt.WA_DeleteOnClose, False)
        self.window.resize(760, 560)
        self.handle = ExampleHandle(self.window, self.snapshot)
        self.handle.controls["controller"] = self
        self.handle.cleanup.append(self.prepare_close)
        self.handle.after_close.append(self.dispose)
        self.panel = self.gui.QWidget(self.window) if main else self.window
        if main:
            self.window.setCentralWidget(self.panel)
        self.layout = self.gui.QVBoxLayout(self.panel)

    def snapshot(self):
        return dict(self.state)

    def prepare_close(self):
        if self.state.get("dragging", False):
            raise RuntimeError("Finish the drag before closing this example")
        self.closing = True

    def dispose(self):
        if self.temporary is not None:
            self.temporary.cleanup()
            self.temporary = None
        self.pending.clear()

    def keep(self, name, obj):
        self.handle.controls[name] = obj
        return obj

    def connect(self, obj, signature, callback):
        def route(*args):
            if not self.closing:
                callback(*args)

        self.handle.connect_old(obj, signature, route)
        return route

    def button(self, name, callback, layout=None):
        button = self.keep(name, self.gui.QPushButton(name, self.panel))
        (layout or self.layout).addWidget(button)
        self.connect(button, "clicked()", lambda *args: callback())
        return button

    def combo(self, name, items, callback, layout=None):
        combo = self.keep(name, self.gui.QComboBox(self.panel))
        combo.addItems(items)
        (layout or self.layout).addWidget(combo)
        self.connect(combo, "currentIndexChanged(int)", lambda i: callback(int(i)))
        return combo

    def timer(self, name, callback, interval, start=True, once=False):
        timer = self.keep(name, self.core.QTimer(self.window))
        timer.setSingleShot(once)
        self.connect(timer, "timeout()", lambda: callback())
        self.handle.cleanup.append(timer.stop)
        if start:
            timer.start(interval)
        return timer

    def root(self):
        if self.temporary is None:
            self.temporary = TemporaryDirectory(prefix="fontlab-example-")
        return Path(self.temporary.name)

    def path(self, filename):
        root = self.root().resolve()
        result = Path(filename).resolve()
        if result == root or not result.is_relative_to(root):
            raise ValueError("Choose a file within the example folder")
        return result

    def dialog(self, dialog):
        from fontlabapp.widgets import OwnedWidget

        dialog.setAttribute(self.core.Qt.WA_QuitOnClose, False)
        self.handle.alerts.append(OwnedWidget(dialog, dialog))
        self.pending.append(dialog)
        dialog.open()
        return dialog

    def message(self, text):
        box = self.gui.QMessageBox(self.window)
        box.setText(str(text))
        return self.dialog(box)

    def choose(self, saving, callback, pattern="All files (*)"):
        box = self.gui.QFileDialog(self.window)
        box.setDirectory(str(self.root()))
        box.setNameFilter(pattern)
        box.setAcceptMode(box.AcceptSave if saving else box.AcceptOpen)

        def selected(filename):
            try:
                callback(str(filename))
            except (OSError, ValueError, UnicodeError) as error:
                self.state["error"] = str(error)
                self.message(str(error))

        self.connect(box, "fileSelected(QString)", selected)
        return self.dialog(box)

    def action(self, menu, name, callback, check=False):
        action = self.keep(name, self.gui.QAction(name, self.window))
        action.setCheckable(check)
        menu.addAction(action)
        self.connect(action, "triggered(bool)", lambda *args: callback())
        return action

    def finish(self):
        return self.handle


def build(qt):
    session = Session(qt, TITLE, MAIN)
    try:
        configure(session)
        return session.finish()
    except BaseException:
        session.handle.close()
        raise


import json


def configure(s):
    gui = s.gui
    contacts = {}
    s.state.update(contacts=contacts, mode="browse", current=None, error="")
    name = s.keep("name", gui.QLineEdit(s.panel))
    address = s.keep("address", gui.QPlainTextEdit(s.panel))
    grid = gui.QGridLayout()
    grid.addWidget(gui.QLabel("Name", s.panel), 0, 0)
    grid.addWidget(name, 0, 1)
    grid.addWidget(gui.QLabel("Address", s.panel), 1, 0)
    grid.addWidget(address, 1, 1)
    s.layout.addLayout(grid)
    previous = ["", ""]
    editing = [None]
    buttons = {}

    def fields():
        return str(value(name, "text")), str(address.toPlainText())

    def display(key):
        s.state["current"] = key
        name.setText(key or "")
        address.setPlainText(contacts.get(key, ""))
        refresh()

    def refresh():
        busy = s.state["mode"] != "browse"
        name.setReadOnly(STAGE > 1 and not busy)
        address.setReadOnly(STAGE > 1 and not busy)
        for label, button in buttons.items():
            enabled = True
            if label in ("Submit", "Cancel"):
                enabled = busy
            elif label in ("Add", "Load"):
                enabled = not busy
            elif label in ("Next", "Previous"):
                enabled = not busy and len(contacts) > 1
            elif label == "Find":
                enabled = not busy and len(contacts) > 2
            else:
                enabled = not busy and bool(contacts)
            button.setEnabled(enabled)

    def start(mode):
        previous[:] = fields()
        editing[0] = s.state["current"] if mode == "edit" else None
        s.state["mode"] = mode
        if mode == "add":
            name.clear()
            address.clear()
        refresh()

    def submit():
        key, text = fields()
        if not key.strip() or not text.strip():
            return s.message("Both fields need text.")
        if key in contacts and key != editing[0]:
            return s.message("That name already belongs to a contact.")
        if editing[0] is not None and editing[0] != key:
            contacts.pop(editing[0])
        contacts[key] = text
        s.state["mode"] = "browse"
        display(key)

    def cancel():
        s.state["mode"] = "browse"
        name.setText(previous[0])
        address.setPlainText(previous[1])
        refresh()

    def navigate(delta):
        keys = sorted(contacts)
        if keys:
            current = s.state["current"]
            index = keys.index(current) if current in keys else 0
            display(keys[(index + delta) % len(keys)])

    def remove(confirmed=None):
        if confirmed is None:
            box = gui.QMessageBox(s.window)
            box.setText("Remove this contact?")
            box.setStandardButtons(gui.QMessageBox.Yes | gui.QMessageBox.No)
            s.connect(
                box,
                "finished(int)",
                lambda result: remove(result == gui.QMessageBox.Yes),
            )
            return s.dialog(box)
        if confirmed:
            contacts.pop(s.state["current"], None)
            display(next(iter(sorted(contacts)), None))

    search = [None]
    query = [None]

    def find_result():
        key = str(value(query[0], "text"))
        if not key:
            return
        if key in contacts:
            display(key)
        else:
            s.message("No contact has that exact name.")
        search[0].hide()

    def find():
        if search[0] is None:
            search[0] = gui.QDialog(s.window)
            search[0].setWindowTitle("Find a name")
            layout = gui.QVBoxLayout(search[0])
            query[0] = s.keep("query", gui.QLineEdit(search[0]))
            layout.addWidget(query[0])
            button = gui.QPushButton("Find", search[0])
            layout.addWidget(button)
            s.connect(button, "clicked()", find_result)
            s.connect(query[0], "returnPressed()", find_result)
            s.dialog(search[0])
        else:
            search[0].show()

    def save_file(filename):
        s.path(filename).write_text(
            json.dumps(contacts, ensure_ascii=False), encoding="utf-8"
        )

    def load_file(filename):
        payload = json.loads(s.path(filename).read_text(encoding="utf-8"))
        if (
            not isinstance(payload, dict)
            or not payload
            or any(
                not isinstance(k, str)
                or not k.strip()
                or not isinstance(v, str)
                or not v.strip()
                for k, v in payload.items()
            )
        ):
            raise ValueError(
                "A collection must contain nonempty text names and addresses"
            )
        contacts.clear()
        contacts.update(payload)
        display(min(contacts))

    def export_file(filename):
        key, text = fields()

        def escape(part):
            return part.replace("\\", "\\\\").replace(";", "\\;")

        address_text = ";".join(escape(line) for line in text.splitlines())
        card = "BEGIN:VCARD\r\nVERSION:2.1\r\nFN;CHARSET=UTF-8:" + escape(key)
        card += "\r\nADR;CHARSET=UTF-8:;;" + address_text + "\r\nEND:VCARD\r\n"
        s.path(filename).write_bytes(card.encode("utf-8"))

    actions = {}
    if STAGE >= 2:
        actions.update(Add=lambda: start("add"), Submit=submit, Cancel=cancel)
    if STAGE >= 3:
        actions.update(Next=lambda: navigate(1), Previous=lambda: navigate(-1))
    if STAGE >= 4:
        actions.update(Edit=lambda: start("edit"), Remove=remove)
    if STAGE >= 5:
        actions["Find"] = find
    if STAGE >= 6:
        actions.update(
            Load=lambda: s.choose(False, load_file),
            Save=lambda: s.choose(True, save_file),
        )
    if STAGE >= 7:
        actions["Export"] = lambda: s.choose(True, export_file, "Contact card (*.vcf)")
    for label, callback in actions.items():
        buttons[label] = s.button(label, callback)
    for key, callback in {
        "submit": submit,
        "cancel": cancel,
        "navigate": navigate,
        "remove": remove,
        "save_file": save_file,
        "load_file": load_file,
        "export_file": export_file,
        "find": find,
        "find_result": find_result,
    }.items():
        required = {
            "navigate": 3,
            "remove": 4,
            "find": 5,
            "find_result": 5,
            "save_file": 6,
            "load_file": 6,
            "export_file": 7,
        }.get(key, 2)
        if STAGE >= required:
            s.keep(key, callback)
    s.keep("contacts", contacts)
    refresh()
