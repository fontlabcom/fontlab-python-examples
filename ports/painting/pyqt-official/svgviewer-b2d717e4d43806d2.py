# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b2d717e4d43806d2.md
# this_file: ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py
TITLE = "Vector scenes"
MAIN = True

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


SVG_SCENES = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="220"><circle cx="110" cy="100" r="75" fill="#2788a4" opacity=".6"/><circle cx="190" cy="120" r="75" fill="#d9ac42" opacity=".6"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="220"><path d="M20 180 C80 0 210 0 280 180 M20 40 C100 210 180 210 280 40" fill="none" stroke="#74469c" stroke-width="12"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="220"><defs><radialGradient id="a"><stop stop-color="#fff"/><stop offset="1" stop-color="#408c75"/></radialGradient></defs><circle cx="100" cy="100" r="70" fill="url(#a)"/><circle cx="220" cy="150" r="50" fill="url(#a)"/></svg>',
)


def configure(s):
    gui, _core = s.gui, s.core
    scene = s.keep("scene", gui.QGraphicsScene(s.window))
    s.state.update(
        filename=None, zoom=1.0, renderer="native", background=True, outline=True
    )

    class View(gui.QGraphicsView):
        def wheelEvent(self, event):
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            zoom(factor)
            event.accept()

    view = s.keep("view", View(scene, s.panel))
    s.layout.addWidget(view)
    items = []

    def zoom(factor):
        if 0.02 < s.state["zoom"] * factor < 100:
            view.scale(factor, factor)
            s.state["zoom"] *= factor

    def open_file(filename):
        import xml.etree.ElementTree as ET

        try:
            root = ET.parse(filename).getroot()
        except ET.ParseError as error:
            raise ValueError("The SVG document is malformed") from error
        if root.tag.split("}")[-1] != "svg":
            raise ValueError("Choose an SVG document")
        renderer = s.qt.QtSvg.QSvgRenderer(str(filename), s.window)
        if not renderer.isValid():
            renderer.deleteLater()
            raise ValueError("The SVG renderer rejected this document")
        vector = s.qt.QtSvg.QGraphicsSvgItem(str(filename))
        bounds = vector.boundingRect()
        scene.clear()
        items.clear()
        scene.addItem(vector)
        outline = gui.QGraphicsRectItem(bounds)
        outline.setPen(gui.QPen(gui.QColor("#353535")))
        scene.addItem(outline)
        outline.setVisible(s.state["outline"])
        image = gui.QImage(
            max(1, int(bounds.width())),
            max(1, int(bounds.height())),
            gui.QImage.Format_ARGB32,
        )
        image.fill(0)
        painter = gui.QPainter(image)
        try:
            renderer.render(painter)
        finally:
            painter.end()
        raster = gui.QGraphicsPixmapItem(gui.QPixmap.fromImage(image))
        scene.addItem(raster)
        raster.setVisible(s.state["renderer"] == "raster")
        vector.setVisible(s.state["renderer"] != "raster")
        items.extend((vector, raster, outline))
        scene.setSceneRect(bounds)
        s.keep("svg", vector)
        s.keep("outline", outline)
        renderer.deleteLater()
        s.state["filename"] = str(filename)
        view.resetTransform()
        s.state["zoom"] = 1.0

    def backend(kind):
        view.setViewport(gui.QWidget(view))
        view.setViewportUpdateMode(gui.QGraphicsView.FullViewportUpdate)
        view.setCacheMode(
            gui.QGraphicsView.CacheBackground
            if kind == "raster"
            else gui.QGraphicsView.CacheNone
        )
        if items:
            items[0].setVisible(kind == "native")
            items[1].setVisible(kind == "raster")
        s.state["renderer"] = kind

    bar = s.window.menuBar()
    file_menu = bar.addMenu("File")
    s.action(file_menu, "Open", lambda: s.choose(False, open_file, "SVG (*.svg)"))
    for index, markup in enumerate(SVG_SCENES):
        path = s.root() / ("scene-" + str(index) + ".svg")
        path.write_text(markup, encoding="utf-8")
        s.action(file_menu, "Scene " + str(index + 1), lambda p=str(path): open_file(p))
    s.action(file_menu, "Exit", s.handle.close)
    options = bar.addMenu("View")

    def toggle_background():
        s.state["background"] = not s.state["background"]
        scene.setBackgroundBrush(
            gui.QBrush(gui.QColor("#eee9dd" if s.state["background"] else "#ffffff"))
        )

    def toggle_outline():
        s.state["outline"] = not s.state["outline"]
        if items:
            items[-1].setVisible(s.state["outline"])

    s.action(options, "Background", toggle_background, True).setChecked(True)
    s.action(options, "Outline", toggle_outline, True).setChecked(True)
    renderer = bar.addMenu("Renderer")
    s.action(renderer, "Native", lambda: backend("native"))
    s.action(renderer, "Raster image", lambda: backend("raster"))
    s.action(renderer, "OpenGL unavailable", lambda: None).setEnabled(False)
    s.keep("open_file", open_file)
    s.keep("zoom", zoom)
    s.keep("backend", backend)
    open_file(str(s.root() / "scene-0.svg"))
