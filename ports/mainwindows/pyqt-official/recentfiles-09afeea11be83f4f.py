# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/09afeea11be83f4f.md
# this_file: ports/mainwindows/pyqt-official/recentfiles-09afeea11be83f4f.py
TITLE = "Owned document workspace"
MAIN = True
MODE = "recent"

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
        icon = self.gui.QPixmap(24, 24)
        icon.fill(self.gui.QColor("#f0eadc"))
        painter = self.gui.QPainter(icon)
        try:
            painter.setPen(self.gui.QPen(self.gui.QColor("#36516d"), 2))
            painter.drawRoundedRect(self.core.QRectF(4, 3, 16, 18), 2.0, 2.0)
            painter.drawText(7, 17, name[:1])
        finally:
            painter.end()
        action.setIcon(self.gui.QIcon(icon))
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


import configparser


def configure(s):
    gui, core = s.gui, s.core
    documents = []
    recent = []
    ini = s.root() / "window.ini"
    settings = configparser.ConfigParser()
    settings["window"] = {"width": "760", "height": "560"}
    with ini.open("w", encoding="utf-8") as stream:
        settings.write(stream)
    s.state.update(documents=[], recent=recent, error="")
    area = None
    if MODE == "mdi":
        area = s.keep("mdi", gui.QMdiArea(s.panel))
        s.layout.addWidget(area)

    def current():
        if area:
            active = area.activeSubWindow()
            return next(
                (d for d in documents if d["window"] is active),
                documents[-1] if documents else None,
            )
        return next(
            (d for d in reversed(documents) if value(d["window"], "isActiveWindow")),
            documents[-1] if documents else None,
        )

    def sync():
        s.state["documents"] = [
            {
                "filename": d["path"],
                "modified": d["modified"],
                "text": str(d["editor"].toPlainText()),
            }
            for d in documents
        ]
        for d in documents:
            title = Path(d["path"]).name if d["path"] else "Untitled"
            d["window"].setWindowTitle(title + (" *" if d["modified"] else ""))
        update_recent()

    def save_document(doc, filename=None, after=None):
        if doc is None:
            return False
        target = filename or doc["path"]
        if not target:
            return s.choose(
                True,
                lambda path: save_document(doc, path, after),
                "Text (*.txt);;All files (*)",
            )
        try:
            text = str(doc["editor"].toPlainText())
            Path(target).write_text(text, encoding="utf-8")
        except (OSError, UnicodeError) as error:
            s.state["error"] = str(error)
            s.message(str(error))
            return False
        doc["path"], doc["modified"] = str(Path(target).resolve()), False
        promote(doc["path"])
        sync()
        if after:
            after()
        return True

    def guard(doc, after, decision=None):
        if doc is None or not doc["modified"]:
            return after()
        if decision == "discard":
            return after()
        if decision == "save":
            return save_document(doc, after=after)
        if decision == "cancel":
            return False
        box = gui.QMessageBox(doc["window"])
        box.setText("Save changes before continuing?")
        box.setStandardButtons(
            gui.QMessageBox.Save | gui.QMessageBox.Discard | gui.QMessageBox.Cancel
        )

        def answer(result):
            choices = {gui.QMessageBox.Save: "save", gui.QMessageBox.Discard: "discard"}
            guard(doc, after, choices.get(result, "cancel"))

        s.connect(box, "finished(int)", answer)
        return s.dialog(box)

    def retire(doc):
        if doc not in documents:
            return
        documents.remove(doc)
        doc["window"].hide()
        sync()

    def close_all():
        if not documents:
            return s.handle.close()
        return guard(documents[-1], lambda: (retire(documents[-1]), close_all()))

    recent_actions = []

    def update_recent():
        for actions in recent_actions:
            for index, action in enumerate(actions):
                available = index < len(recent)
                action.setVisible(available)
                if available:
                    action.setText(str(index + 1) + " " + recent[index])

    def promote(filename):
        if filename in recent:
            recent.remove(filename)
        recent.insert(0, filename)
        del recent[5:]
        settings["recent"] = {str(i): p for i, p in enumerate(recent)}
        with ini.open("w", encoding="utf-8") as stream:
            settings.write(stream)
        update_recent()

    def open_file(filename):
        filename = str(Path(filename).resolve())
        duplicate = next((d for d in documents if d["path"] == filename), None)
        if duplicate:
            if area:
                area.setActiveSubWindow(duplicate["window"])
            duplicate["window"].show()
            duplicate["window"].raise_()
            duplicate["window"].activateWindow()
            return duplicate
        try:
            text = Path(filename).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            s.state["error"] = str(error)
            s.message(str(error))
            return None

        def loaded():
            doc = current() if MODE in ("application", "dock") else None
            if doc is not None:
                doc["editor"].setPlainText(text)
                doc.update(path=filename, modified=False)
            else:
                doc = new_document(text, filename)
            promote(filename)
            sync()
            return doc

        if MODE in ("application", "dock"):
            return guard(current(), loaded)
        return loaded()

    def menu_for(window, doc):
        bar = window.menuBar()
        file_menu = bar.addMenu("File")
        toolbar = window.addToolBar("File")

        def add(menu, label, callback, shortcut=None):
            action = gui.QAction(label, window)
            icon = gui.QPixmap(24, 24)
            icon.fill(gui.QColor("#f0eadc"))
            painter = gui.QPainter(icon)
            try:
                painter.drawRect(4, 3, 16, 18)
                painter.drawText(7, 17, label[:1])
            finally:
                painter.end()
            action.setIcon(gui.QIcon(icon))
            menu.addAction(action)
            toolbar.addAction(action)
            if shortcut:
                action.setShortcut(shortcut)
            s.connect(action, "triggered(bool)", lambda *args: callback())
            s.keep(label + str(len(documents)), action)
            return action

        add(file_menu, "New", new, "Ctrl+N")
        add(file_menu, "Open", lambda: s.choose(False, open_file), "Ctrl+O")
        add(file_menu, "Save", lambda: save_document(doc), "Ctrl+S")
        add(
            file_menu,
            "Save As",
            lambda: s.choose(True, lambda p: save_document(doc, p)),
        )
        add(file_menu, "Close", lambda: guard(doc, lambda: retire(doc)))
        add(file_menu, "Exit", close_all)
        if MODE == "recent":
            actions = []
            for index in range(5):
                action = add(
                    file_menu,
                    "Recent " + str(index + 1),
                    lambda i=index: open_file(recent[i]) if i < len(recent) else None,
                )
                actions.append(action)
            recent_actions.append(actions)
        edit = bar.addMenu("Edit")
        editor = doc["editor"]
        for label, method in [
            ("Undo", editor.undo),
            ("Cut", editor.cut),
            ("Copy", editor.copy),
            ("Paste", editor.paste),
        ]:
            action = add(edit, label, method)
            if label in ("Cut", "Copy"):
                action.setEnabled(False)
                s.connect(
                    editor,
                    "copyAvailable(bool)",
                    lambda enabled, a=action: a.setEnabled(enabled),
                )
        help_menu = bar.addMenu("Help")
        add(help_menu, "About", lambda: s.message("An owned text workspace."))
        window.statusBar().showMessage("Ready")

    def new_document(text="", filename=None):
        if area:

            class Child(gui.QMdiSubWindow):
                def closeEvent(self, event):
                    event.ignore()
                    guard(doc, lambda: retire(doc))

            window = Child()
            editor = gui.QPlainTextEdit(window)
            window.setWidget(editor)
            area.addSubWindow(window)
            window.setAttribute(core.Qt.WA_DeleteOnClose, False)
        elif not documents and MODE in ("application", "dock"):
            window = s.window
            editor = (
                gui.QTextEdit(s.panel)
                if MODE == "dock"
                else gui.QPlainTextEdit(s.panel)
            )
            s.layout.addWidget(editor)
        else:

            class Child(gui.QMainWindow):
                def closeEvent(self, event):
                    event.ignore()
                    guard(doc, lambda: retire(doc))

            window = Child()
            window.setAttribute(core.Qt.WA_QuitOnClose, False)
            window.setAttribute(core.Qt.WA_DeleteOnClose, False)
            editor = gui.QPlainTextEdit(window)
            window.setCentralWidget(editor)
            from fontlabapp.widgets import OwnedWidget

            s.handle.alerts.append(OwnedWidget(window, window))
        doc = {"window": window, "editor": editor, "path": filename, "modified": False}
        documents.append(doc)
        s.keep("editor", editor)
        s.keep("window" + str(id(doc)), window)
        editor.setPlainText(text)

        def changed():
            doc["modified"] = True
            sync()

        s.connect(editor, "textChanged()", changed)
        if not area:
            menu_for(window, doc)
        window.show()
        sync()
        return doc

    def new():
        if MODE in ("application", "dock") and current():
            doc = current()

            def clear():
                doc["editor"].clear()
                doc.update(path=None, modified=False)
                sync()

            return guard(doc, clear)
        return new_document()

    if area:
        # MDI actions select the active editor at activation time.
        menu = s.window.menuBar().addMenu("File")
        for label, callback in [
            ("New", new),
            ("Open", lambda: s.choose(False, open_file)),
            ("Save", lambda: save_document(current())),
            ("Save As", lambda: s.choose(True, lambda p: save_document(current(), p))),
            ("Exit", close_all),
        ]:
            s.action(menu, label, callback)
        edit = s.window.menuBar().addMenu("Edit")
        for label, method in [("Cut", "cut"), ("Copy", "copy"), ("Paste", "paste")]:
            s.action(
                edit,
                label,
                lambda m=method: (
                    getattr(current()["editor"], m)() if current() else None
                ),
            )
        windows = s.window.menuBar().addMenu("Window")
        for label, callback in [
            ("Tile", area.tileSubWindows),
            ("Cascade", area.cascadeSubWindows),
            ("Next", area.activateNextSubWindow),
            ("Previous", area.activatePreviousSubWindow),
            ("Close", lambda: guard(current(), lambda: retire(current()))),
            ("Close All", close_all),
        ]:
            s.action(windows, label, callback)

        def list_windows():
            for action in list(value(windows, "actions"))[6:]:
                windows.removeAction(action)
                for obj, signature, callback in list(s.handle.connections):
                    if obj is action:
                        obj.disconnect(signature, callback)
                        s.handle.connections.remove((obj, signature, callback))
                action.deleteLater()
            for doc in documents:
                action = gui.QAction(doc["path"] or "Untitled", s.window)
                windows.addAction(action)
                # Receiver window is retained by its signal; teardown disconnects.
                s.connect(
                    action,
                    "triggered(bool)",
                    lambda *args, d=doc: area.setActiveSubWindow(d["window"]),
                )

        s.connect(windows, "aboutToShow()", list_windows)
        s.window.menuBar().addMenu("Help")
        s.window.addToolBar("Documents")
        s.window.statusBar().showMessage("Owned documents")
    s.before_close = close_all
    first = new_document()
    if MODE in ("sdi", "recent"):
        # Use the launcher-owned outer window for the first document too.
        child = first["window"]
        first["window"] = s.window
        s.window.setCentralWidget(first["editor"])
        menu_for(s.window, first)
        child.hide()
    if MODE == "dock":
        editor = first["editor"]
        editor.setPlainText(
            "Dear reader,\n\nThank you for writing.\n\nKind regards,\nThe studio"
        )
        first["modified"] = False
        view = s.window.menuBar().addMenu("View")
        for title, entries in [
            ("Customers", ["Rowan Vale", "Aster Studio", "Juniper Works"]),
            (
                "Paragraphs",
                [
                    "The revised proof is ready.",
                    "Please send your preferred date.",
                    "We appreciate the careful notes.",
                ],
            ),
        ]:
            dock = s.keep(title, gui.QDockWidget(title, s.window))
            listing = gui.QListWidget(dock)
            listing.addItems(entries)
            dock.setWidget(listing)
            s.window.addDockWidget(core.Qt.RightDockWidgetArea, dock)
            view.addAction(dock.toggleViewAction())
            s.connect(
                listing,
                "itemActivated(QListWidgetItem*)",
                lambda item: editor.insertPlainText(str(value(item, "text")) + "\n"),
            )
        file_menu = s.window.menuBar().addMenu("Output")

        def html_save(filename):
            Path(filename).write_text(str(editor.toHtml()), encoding="utf-8")

        s.action(
            file_menu, "Save HTML", lambda: s.choose(True, html_save, "HTML (*.html)")
        )

        def print_document():
            printer = qt_printer = gui.QPrinter()
            qt_printer.setOutputFormat(qt_printer.PdfFormat)
            qt_printer.setOutputFileName(str(s.root() / "letter.pdf"))
            dialog = gui.QPrintDialog(printer, s.window)
            s.keep("printer", printer)
            s.connect(dialog, "accepted()", lambda: editor.print_(printer))
            s.dialog(dialog)

        s.action(file_menu, "Print", print_document)
    for key, callback in {
        "new_document": new_document,
        "open_file": open_file,
        "save_document": save_document,
        "guard": guard,
        "close_all": close_all,
        "current": current,
        "promote": promote,
    }.items():
        s.keep(key, callback)
    s.keep("documents", documents)
