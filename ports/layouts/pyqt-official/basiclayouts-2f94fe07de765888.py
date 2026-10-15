# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/2f94fe07de765888.md
# this_file: ports/layouts/pyqt-official/basiclayouts-2f94fe07de765888.py
"""Basic layout gallery and new batch-local ownership primitives."""

from pathlib import Path
from tempfile import TemporaryDirectory

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    result = getattr(obj, name)
    return result() if callable(result) else result


def port(relative):
    """Load another freshly written batch module, without catalog state changes."""
    from importlib import util

    path = Path(__file__).resolve().parents[2] / relative
    spec = util.spec_from_file_location("cleanroom_component_" + path.stem, path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Session:
    """Keep Python state outside wrappers and close partially built UI."""

    def __init__(self, qt, title, window=None):
        self.qt, self.g, self.c = qt, qt.QtGui, qt.QtCore
        self.window = window if window is not None else self.g.QWidget()
        self.h = ExampleHandle(self.window, self.snapshot)
        self.state, self.controls = {}, self.h.controls
        self._temp, self.layout = None, None
        self.window.setWindowTitle(title)
        self.window.setAttribute(self.c.Qt.WA_QuitOnClose, False)
        self.window.setAttribute(self.c.Qt.WA_DeleteOnClose, False)
        self.window.resize(640, 460)

    def __enter__(self):
        return self

    def __exit__(self, kind, error, traceback):
        if kind:
            self.h.close()

    def snapshot(self):
        result = dict(self.state)
        for key, obj in self.controls.items():
            for name in ("text", "value", "currentIndex", "checked"):
                prop = getattr(obj, name, None)
                if isinstance(prop, (str, int, float, bool)):
                    result[key + "_" + name] = prop
        return result

    def keep(self, key, obj):
        self.controls[key] = obj
        return obj

    def link(self, obj, signal, callback):
        def routed(*args):
            if not self.h.owner.closed:
                callback(*args)

        self.h.connect_old(obj, signal, routed)
        return routed

    def vertical(self, parent=None):
        parent = self.window if parent is None else parent
        layout = self.g.QVBoxLayout(parent)
        if parent is self.window:
            self.layout = layout
        return layout

    def add(self, obj, layout=None):
        (layout if layout is not None else self.layout).addWidget(obj)
        return obj

    def label(self, text, layout=None):
        return self.add(self.g.QLabel(text, self.window), layout)

    def line(self, key, text="", layout=None):
        return self.add(self.keep(key, self.g.QLineEdit(text, self.window)), layout)

    def check(self, key, text, checked=False, layout=None):
        obj = self.keep(key, self.g.QCheckBox(text, self.window))
        obj.setChecked(checked)
        return self.add(obj, layout)

    def spin(self, key, low=0, high=99, initial=0, layout=None, decimal=False):
        obj = self.keep(
            key, (self.g.QDoubleSpinBox if decimal else self.g.QSpinBox)(self.window)
        )
        obj.setRange(low, high)
        obj.setValue(initial)
        return self.add(obj, layout)

    def combo(self, key, items, layout=None):
        obj = self.keep(key, self.g.QComboBox(self.window))
        obj.addItems(list(items))
        return self.add(obj, layout)

    def button(self, key, text, callback=None, layout=None):
        obj = self.keep(key, self.g.QPushButton(text, self.window))
        self.add(obj, layout)
        if callback is not None:
            self.link(obj, "clicked()", lambda *a: callback())
        return obj

    def timer(self, key, interval, callback, single=False, start=True):
        timer = self.keep(key, self.c.QTimer(self.window))
        timer.setSingleShot(single)
        self.link(timer, "timeout()", lambda *a: callback())
        self.h.cleanup.append(lambda: timer.stop() if not self.h.owner.closed else None)
        if start:
            timer.start(interval)
        return timer

    def temp(self):
        if self._temp is None:
            self._temp = TemporaryDirectory(prefix="fontlab-example-")
            self.h.after_close.append(self._temp.cleanup)
        return Path(self._temp.name)

    def alert(self, dialog):
        from fontlabapp.widgets import OwnedWidget

        dialog.setAttribute(self.c.Qt.WA_QuitOnClose, False)
        dialog.setAttribute(self.c.Qt.WA_DeleteOnClose, False)
        self.h.alerts.append(OwnedWidget(dialog, dialog))
        return dialog

    def choose(self, callback, save=False, directory=False):
        dialog = self.keep("file_dialog", self.alert(self.g.QFileDialog(self.window)))
        dialog.setOption(self.g.QFileDialog.DontUseNativeDialog, True)
        if directory:
            dialog.setFileMode(self.g.QFileDialog.Directory)
        elif save:
            dialog.setAcceptMode(self.g.QFileDialog.AcceptSave)
        else:
            dialog.setFileMode(self.g.QFileDialog.ExistingFile)
        dialog.setDirectory(str(self.temp()))

        def selected(*args):
            files = list(dialog.selectedFiles())
            if files:
                try:
                    callback(str(files[0]))
                except (OSError, ValueError) as error:
                    self.state["error"] = str(error)

        self.link(dialog, "accepted()", selected)
        dialog.open()
        return dialog

    def menu(self, title, entries):
        if "menu_bar" not in self.controls:
            bar = self.keep("menu_bar", self.g.QMenuBar(self.window))
            self.layout.setMenuBar(bar)
        menu = self.controls["menu_bar"].addMenu(title)
        for label, callback in entries:
            action = self.g.QAction(label, self.window)
            menu.addAction(action)
            self.keep("action_" + label, action)
            self.link(action, "triggered()", lambda *a, cb=callback: cb())
        return menu

    def table(self, key, headers, rows, layout=None):
        table = self.keep(
            key, self.g.QTableWidget(len(rows), len(headers), self.window)
        )
        table.setHorizontalHeaderLabels(headers)
        for r, row in enumerate(rows):
            for col, cell in enumerate(row):
                table.setItem(r, col, self.g.QTableWidgetItem(str(cell)))
        return self.add(table, layout)

    def model(self, headers, rows):
        model = self.g.QStandardItemModel(self.window)
        model.setHorizontalHeaderLabels(headers)
        for row in rows:
            model.appendRow([self.g.QStandardItem(str(cell)) for cell in row])
        self.h.model = model
        return self.keep("model", model)

    def view(self, key, model, kind="QTableView", layout=None):
        view = self.keep(key, getattr(self.g, kind)(self.window))
        view.setModel(model)
        self.add(view, layout)
        self.h.release.append(
            lambda: view.setModel(None) if not self.h.owner.closed else None
        )
        return view

    def local_style(self, name, widgets=None):
        style = self.g.QStyleFactory.create(name)
        if style is not None:
            style.setParent(self.window)
            self.keep("style", style)
            for widget in widgets or [self.window]:
                widget.setStyle(style)


def canvas(s, paint, events=None):
    events = events or {}
    g = s.g

    class Surface(g.QWidget):
        def paintEvent(self, event):
            painter = g.QPainter(self)
            try:
                painter.setRenderHint(g.QPainter.Antialiasing)
                paint(painter, int(value(self, "width")), int(value(self, "height")))
            finally:
                painter.end()

        def mousePressEvent(self, event):
            if "press" in events:
                events["press"](event)
            else:
                g.QWidget.mousePressEvent(self, event)

        def mouseMoveEvent(self, event):
            if "move" in events:
                events["move"](event)
            else:
                g.QWidget.mouseMoveEvent(self, event)

        def mouseReleaseEvent(self, event):
            if "release" in events:
                events["release"](event)
            else:
                g.QWidget.mouseReleaseEvent(self, event)

        def resizeEvent(self, event):
            g.QWidget.resizeEvent(self, event)
            if "resize" in events:
                events["resize"](event)

        def keyPressEvent(self, event):
            if "key" in events:
                events["key"](event)
            else:
                g.QWidget.keyPressEvent(self, event)

        def contextMenuEvent(self, event):
            if "context" in events:
                events["context"](event)
            else:
                g.QWidget.contextMenuEvent(self, event)

    surface = s.keep("canvas", Surface(s.window))
    surface.setMinimumSize(100, 100)
    surface.setMouseTracking(True)
    surface.setFocusPolicy(s.c.Qt.StrongFocus)
    s.h.callbacks.extend([paint, *events.values()])
    return surface


def pictogram(s, color="#317e99", size=32):
    pix = s.g.QPixmap(size, size)
    pix.fill(s.g.QColor(0, 0, 0, 0))
    painter = s.g.QPainter(pix)
    try:
        painter.setBrush(s.g.QColor(color))
        painter.drawEllipse(3, 3, size - 6, size - 6)
        painter.setPen(s.g.QColor("white"))
        painter.drawLine(8, size // 2, size - 8, size // 2)
    finally:
        painter.end()
    return pix


def build(qt):
    with Session(qt, "Basic layout gallery", qt.QtGui.QDialog()) as s:
        s.vertical()
        s.menu("File", [("Exit", s.h.close)])
        for title, kind in [
            ("Actions", "QHBoxLayout"),
            ("Grid", "QGridLayout"),
            ("Fields", "QFormLayout"),
        ]:
            group = s.g.QGroupBox(title, s.window)
            layout = getattr(s.g, kind)(group)
            if kind == "QHBoxLayout":
                for text in ("First", "Second", "Third"):
                    layout.addWidget(s.g.QPushButton(text, group))
            elif kind == "QGridLayout":
                for i in range(3):
                    layout.addWidget(s.g.QLabel("Value " + str(i + 1), group), i, 0)
                    layout.addWidget(s.g.QLineEdit(group), i, 1)
                layout.addWidget(
                    s.g.QTextEdit("Notes occupy the wide column.", group), 0, 2, 3, 1
                )
                layout.setColumnStretch(2, 2)
            else:
                for name in ("Name", "Location", "Comment"):
                    layout.addRow(name, s.g.QLineEdit(group))
            s.add(group)
        s.add(s.g.QTextEdit("Resize this window and edit the fields.", s.window))
        s.button("ok", "OK", s.h.close)
        s.button("cancel", "Cancel", s.h.close)
        return s.h
