# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/bd6c8feb783ba845.md
# this_file: ports/animation/pyqt-official/easing-bd6c8feb783ba845.py

from contextlib import contextmanager

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


import math


def embed(qt, scene, widget):
    proxy = qt.QtGui.QGraphicsProxyWidget()
    proxy.setWidget(widget)
    scene.addItem(proxy)
    return proxy


def scene_view(qt, handle, layout):
    scene = qt.QtGui.QGraphicsScene(handle.widget)
    scene.setSceneRect(0, 0, 640, 420)
    view = qt.QtGui.QGraphicsView(scene, handle.widget)
    view.setRenderHint(qt.QtGui.QPainter.Antialiasing, True)
    layout.addWidget(view)
    handle.controls.update(scene=scene, view=view)
    return scene


def emblem(qt, color, index=0):
    pixmap = qt.QtGui.QPixmap(40, 40)
    pixmap.fill(qt.QtGui.QColor(color))
    painter = qt.QtGui.QPainter(pixmap)
    try:
        painter.setPen(qt.QtGui.QPen(qt.QtGui.QColor("white")))
        painter.drawEllipse(7 + index % 4, 7, 24, 24)
        painter.drawLine(8, 30, 30, 8 + index % 8)
    finally:
        painter.end()
    return pixmap


import time

CURVES = (
    ["Linear"]
    + [
        direction + family
        for family in (
            "Quad",
            "Cubic",
            "Quart",
            "Quint",
            "Sine",
            "Expo",
            "Circ",
            "Elastic",
            "Back",
            "Bounce",
        )
        for direction in ("In", "Out", "InOut", "OutIn")
    ]
    + ["InCurve", "OutCurve", "SineCurve", "CosineCurve", "BezierSpline", "TCBSpline"]
)


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Easing gallery") as (handle, layout):
        scene = scene_view(qt, handle, layout)
        label = gui.QLabel()
        label.setPixmap(emblem(qt, "#4c789f"))
        moving = embed(qt, scene, label)
        curves = gui.QListWidget(handle.widget)
        layout.addWidget(curves)
        path = gui.QComboBox(handle.widget)
        path.addItems(["Straight", "Circle"])
        layout.addWidget(path)
        controls = {}
        for name, initial in (("period", 0.3), ("amplitude", 1.0), ("overshoot", 1.7)):
            layout.addWidget(gui.QLabel(name, handle.widget))
            spin = gui.QDoubleSpinBox(handle.widget)
            spin.setRange(0.01, 10.0)
            spin.setSingleStep(0.1)
            spin.setValue(initial)
            controls[name] = spin
            layout.addWidget(spin)
        state = {"curve": None, "started": time.monotonic(), "progress": 0.0}

        def make_curve(name):
            curve = core.QEasingCurve(getattr(core.QEasingCurve, name))
            for prop, spin in controls.items():
                getattr(curve, "set" + prop.title())(float(value(spin, "value")))
            return curve

        def thumbnail(name):
            pixmap = gui.QPixmap(100, 50)
            pixmap.fill(gui.QColor("#fafafa"))
            painter = gui.QPainter(pixmap)
            try:
                painter.setPen(gui.QPen(gui.QColor("#31678c")))
                curve = make_curve(name)
                last = core.QPointF(0, 45 - 38 * curve.valueForProgress(0.0))
                for index in range(1, 41):
                    point = core.QPointF(
                        index * 2.4, 45 - 38 * curve.valueForProgress(index / 40)
                    )
                    painter.drawLine(last, point)
                    last = point
            finally:
                painter.end()
            return gui.QIcon(pixmap)

        for name in CURVES:
            curves.addItem(gui.QListWidgetItem(thumbnail(name), name))

        def reset(*args):
            row = max(0, int(value(curves, "currentRow")))
            state["curve"] = make_curve(CURVES[row])
            state["started"] = time.monotonic()

        def advance():
            progress = ((time.monotonic() - state["started"]) % 2.0) / 2.0
            eased = state["curve"].valueForProgress(progress)
            state["progress"] = float(eased)
            if int(value(path, "currentIndex")) == 0:
                moving.setPos(40 + 500 * eased, 190)
            else:
                angle = 2 * math.pi * eased
                moving.setPos(300 + 150 * math.cos(angle), 190 + 150 * math.sin(angle))

        wire(handle, curves, "currentRowChanged(int)", reset)
        wire(handle, path, "currentIndexChanged(int)", reset)
        for spin in controls.values():
            wire(handle, spin, "valueChanged(double)", reset)
        curves.setCurrentRow(0)
        reset()
        ticker = timer(qt, handle, 16, advance)
        handle.controls.update(
            controls, curves=curves, path=path, moving=moving, timer=ticker
        )
        handle.inspect_ui = lambda: {
            "curves": len(CURVES),
            "selected": CURVES[max(0, int(value(curves, "currentRow")))],
            "progress": state["progress"],
        }
        return handle
