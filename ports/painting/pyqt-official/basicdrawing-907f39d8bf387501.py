# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/907f39d8bf387501.md
# this_file: ports/painting/pyqt-official/basicdrawing-907f39d8bf387501.py
TITLE = "Painter exploration"
MAIN = False
KIND = "basic"

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


def configure(s):
    gui, core = s.gui, s.core
    s.state.update(
        shape=0,
        width=2,
        rotation=0,
        antialias=True,
        transform=False,
        pen=0,
        cap=0,
        join=0,
        brush=0,
        fill=0,
        color1="#4d8db8",
        color2="#e9bd5b",
        operations=[0, 0, 0],
        frame=0,
        paints=0,
    )
    shapes = [
        "Polygon",
        "Rectangle",
        "Rounded rectangle",
        "Ellipse",
        "Pie / chord",
        "Path",
        "Line",
        "Polyline",
        "Arc",
        "Points",
        "Text",
        "Bitmap",
        "Chord",
    ]
    emblem = gui.QPixmap(48, 48)
    emblem.fill(gui.QColor("#f2dfaa"))
    p = gui.QPainter(emblem)
    try:
        p.setBrush(gui.QBrush(gui.QColor("#308c87")))
        p.drawEllipse(6, 6, 36, 36)
        p.drawLine(8, 38, 38, 8)
    finally:
        p.end()
    texture = gui.QPixmap(32, 24)
    texture.fill(gui.QColor("#c6b2a2"))
    p = gui.QPainter(texture)
    try:
        p.drawLine(0, 12, 32, 12)
        p.drawLine(16, 0, 16, 12)
        p.drawLine(0, 12, 0, 24)
    finally:
        p.end()

    def path_for(index):
        path = gui.QPainterPath()
        if index % 3 == 0:
            path.addRect(10.0, 10.0, 65.0, 55.0)
            path.addEllipse(30.0, 20.0, 55.0, 55.0)
        elif index % 3 == 1:
            path.moveTo(10.0, 70.0)
            path.cubicTo(15.0, -15.0, 65.0, 110.0, 85.0, 10.0)
            if index > 3:
                path.closeSubpath()
        else:
            path.addText(5.0, 60.0, gui.QFont("Sans", 26), "Ag")
        path.setFillRule(
            core.Qt.OddEvenFill if s.state["fill"] == 0 else core.Qt.WindingFill
        )
        return path

    def transform(painter, operation):
        if operation == 1:
            painter.rotate(60.0)
        elif operation == 2:
            painter.scale(0.75, 0.75)
        elif operation == 3:
            painter.translate(50.0, 50.0)

    def render(painter, index):
        state = s.state
        painter.setRenderHint(gui.QPainter.Antialiasing, bool(state["antialias"]))
        pen = gui.QPen(gui.QColor("#26374b"))
        pen.setWidth(int(state["width"]))
        styles = [core.Qt.SolidLine, core.Qt.DashLine, core.Qt.DotLine, core.Qt.NoPen]
        pen.setStyle(styles[state["pen"]])
        pen.setCapStyle(
            [core.Qt.FlatCap, core.Qt.SquareCap, core.Qt.RoundCap][state["cap"]]
        )
        pen.setJoinStyle(
            [core.Qt.MiterJoin, core.Qt.BevelJoin, core.Qt.RoundJoin][state["join"]]
        )
        painter.setPen(pen)
        gradient = gui.QLinearGradient(0.0, 0.0, 100.0, 100.0)
        gradient.setColorAt(0.0, gui.QColor(state["color1"]))
        gradient.setColorAt(1.0, gui.QColor(state["color2"]))
        brush = gui.QBrush(gui.QColor(state["color1"]))
        brush_styles = [
            core.Qt.SolidPattern,
            core.Qt.Dense4Pattern,
            core.Qt.CrossPattern,
            core.Qt.BDiagPattern,
            core.Qt.NoBrush,
        ]
        if state["brush"] < 5:
            brush.setStyle(brush_styles[state["brush"]])
        elif state["brush"] == 5:
            brush = gui.QBrush(gradient)
        elif state["brush"] == 6:
            radial = gui.QRadialGradient(50.0, 50.0, 60.0)
            radial.setColorAt(0.0, gui.QColor(state["color1"]))
            radial.setColorAt(1.0, gui.QColor(state["color2"]))
            brush = gui.QBrush(radial)
        else:
            brush = gui.QBrush(texture)
        painter.setBrush(brush)
        if KIND == "circles":
            painter.setRenderHint(gui.QPainter.Antialiasing, index >= 2)
            painter.drawText(
                0,
                -8,
                ("Float" if index % 2 else "Integer")
                + (" · smooth" if index >= 2 else " · aliased"),
            )
            for ring in range(10):
                diameter = float((state["frame"] + ring * 14) % 130) + 0.5
                color = gui.QColor("#267eab")
                color.setAlpha(max(0, 255 - int(diameter * 1.7)))
                painter.setPen(gui.QPen(color))
                painter.setBrush(gui.QBrush(core.Qt.NoBrush))
                rect = core.QRectF(
                    65.0 - diameter / 2, 65.0 - diameter / 2, diameter, diameter
                )
                painter.drawEllipse(rect if index % 2 else rect.toRect())
            return
        if KIND == "transformations":
            painter.drawLine(-40, 0, 130, 0)
            painter.drawLine(0, -40, 0, 130)
            painter.save()
            painter.setPen(gui.QPen(gui.QColor("#b5b5b5")))
            painter.setBrush(gui.QBrush(core.Qt.NoBrush))
            painter.drawRect(0, 0, 90, 70)
            painter.restore()
            for operation in state["operations"][:index]:
                transform(painter, operation)
            shape = state["shape"]
            if shape == 0:
                painter.drawEllipse(5, 5, 70, 70)
                painter.drawLine(40, 40, 40, 15)
                painter.drawLine(40, 40, 65, 40)
            elif shape == 1:
                path = gui.QPainterPath()
                path.moveTo(0.0, 40.0)
                path.lineTo(45.0, 0.0)
                path.lineTo(90.0, 40.0)
                path.lineTo(90.0, 90.0)
                path.lineTo(0.0, 90.0)
                path.closeSubpath()
                painter.drawPath(path)
            elif shape == 2:
                painter.drawText(0, 45, "River")
            else:
                painter.drawRoundedRect(core.QRectF(0, 25, 90, 40), 8.0, 8.0)
                painter.drawEllipse(12, 55, 20, 20)
                painter.drawEllipse(62, 55, 20, 20)
            return
        painter.rotate(float(state["rotation"]))
        if state["transform"]:
            painter.translate(15.0, 8.0)
            painter.rotate(18.0)
            painter.scale(0.8, 0.8)
        if KIND == "paths":
            painter.setBrush(gui.QBrush(gradient))
            painter.drawPath(path_for(index))
            return
        shape = state["shape"]
        points = gui.QPolygonF(
            [
                core.QPointF(10, 65),
                core.QPointF(35, 10),
                core.QPointF(60, 55),
                core.QPointF(85, 20),
            ]
        )
        rect = core.QRectF(10, 10, 75, 65)
        if shape == 0:
            painter.drawPolygon(points)
        elif shape == 1:
            painter.drawRect(rect)
        elif shape == 2:
            painter.drawRoundedRect(rect, 12.0, 12.0)
        elif shape == 3:
            painter.drawEllipse(rect)
        elif shape == 4:
            painter.drawPie(rect, 25 * 16, 250 * 16)
        elif shape == 5:
            painter.drawPath(path_for(1))
        elif shape == 6:
            painter.drawLine(10, 10, 85, 75)
        elif shape == 7:
            painter.drawPolyline(points)
        elif shape == 8:
            painter.drawArc(rect, 25 * 16, 250 * 16)
        elif shape == 9:
            painter.drawPoints(points)
        elif shape == 10:
            painter.drawText(10, 45, "Field")
        elif shape == 11:
            painter.drawPixmap(20, 20, emblem)
        else:
            painter.drawChord(rect, 25 * 16, 250 * 16)

    class Canvas(gui.QWidget):
        def paintEvent(self, event):
            gui.QWidget.paintEvent(self, event)
            painter = gui.QPainter(self)
            try:
                painter.fillRect(value(self, "rect"), gui.QColor("#fbfaf6"))
                count = (
                    9
                    if KIND == "paths"
                    else 4
                    if KIND in ("circles", "transformations")
                    else 12
                )
                columns = 3 if KIND in ("paths", "basic") else 2
                for index in range(count):
                    painter.save()
                    painter.translate(
                        35.0 + index % columns * 170.0, 40.0 + index // columns * 145.0
                    )
                    render(painter, index)
                    painter.restore()
                s.state["paints"] += 1
            finally:
                painter.end()

    canvas = s.keep("canvas", Canvas(s.panel))
    canvas.setMinimumSize(540, 340)
    s.layout.addWidget(canvas)

    def set_option(key, val):
        s.state[key] = val
        canvas.update()

    s.keep("set_option", set_option)
    s.keep("render", render)
    if KIND == "circles":

        def tick():
            s.state["frame"] = (s.state["frame"] + 2) % 130
            canvas.update()

        s.timer("animation", tick, 30)
        return
    s.combo(
        "Shape",
        ["Clock", "House", "Text", "Vehicle"] if KIND == "transformations" else shapes,
        lambda index: set_option("shape", index),
    )
    if KIND == "transformations":
        for index in range(3):

            def operation(option, i=index):
                s.state["operations"][i] = option
                canvas.update()

            s.combo(
                "Operation " + str(index + 1),
                ["Identity", "Rotate 60°", "Scale 0.75", "Translate 50,50"],
                operation,
            )
        return
    for key, label, maximum in [
        ("width", "Line width", 20),
        ("rotation", "Rotation", 360),
    ]:
        spin = s.keep(label, gui.QSpinBox(s.panel))
        spin.setRange(0, maximum)
        spin.setValue(s.state[key])
        s.layout.addWidget(spin)
        s.connect(
            spin, "valueChanged(int)", lambda number, k=key: set_option(k, int(number))
        )
    s.combo("Pen", ["Solid", "Dash", "Dot", "None"], lambda i: set_option("pen", i))
    s.combo("Cap", ["Flat", "Square", "Round"], lambda i: set_option("cap", i))
    s.combo("Join", ["Miter", "Bevel", "Round"], lambda i: set_option("join", i))
    s.combo(
        "Brush",
        ["Solid", "Dense", "Cross", "Diagonal", "Empty", "Linear", "Radial", "Texture"],
        lambda i: set_option("brush", i),
    )
    s.combo("Fill rule", ["Odd-even", "Winding"], lambda i: set_option("fill", i))
    for key in ("color1", "color2"):
        s.combo(
            key,
            ["#4d8db8", "#e9bd5b", "#b7618a", "#4b9c75"],
            lambda i, k=key: set_option(
                k, ["#4d8db8", "#e9bd5b", "#b7618a", "#4b9c75"][i]
            ),
        )
    for key, label in [("antialias", "Antialias"), ("transform", "Transform")]:
        toggle = s.keep(label, gui.QCheckBox(label, s.panel))
        toggle.setChecked(s.state[key])
        s.layout.addWidget(toggle)
        s.connect(
            toggle, "toggled(bool)", lambda checked, k=key: set_option(k, bool(checked))
        )
