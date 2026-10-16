# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c82d1af7d1a7b0cf.md
# this_file: ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py

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


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Painter: raster and OpenGL") as (handle, layout):
        state = {"phase": 0}

        def paint(canvas):
            painter = gui.QPainter(canvas)
            try:
                painter.setRenderHint(gui.QPainter.Antialiasing, True)
                painter.fillRect(
                    value(canvas, "rect"), gui.QBrush(gui.QColor("#f6f2e8"))
                )
                width, height = (
                    float(value(canvas, "width")),
                    float(value(canvas, "height")),
                )
                phase = state["phase"] / 20
                for index in range(30):
                    angle = phase + index * 2 * math.pi / 30
                    radius = 30 + index * 2.5
                    painter.setBrush(
                        gui.QBrush(gui.QColor.fromHsv(index * 12, 175, 210))
                    )
                    painter.drawEllipse(
                        core.QPointF(
                            width / 2 + radius * math.cos(angle),
                            height / 2 + radius * math.sin(angle),
                        ),
                        6 + index / 5,
                        6 + index / 5,
                    )
                painter.setPen(gui.QPen(gui.QColor("#263a50")))
                painter.drawText(16, 30, "Circles in a shared rhythm — Aa Ω 123")
            finally:
                painter.end()

        class Raster(gui.QWidget):
            def paintEvent(self, event):
                paint(self)

        class OpenGL(gui.QOpenGLWidget):
            def paintGL(self):
                paint(self)

        raster, gl = Raster(handle.widget), OpenGL(handle.widget)
        format = gui.QSurfaceFormat()
        format.setSamples(4)
        gl.setFormat(format)
        layout.addWidget(gui.QLabel("QWidget renderer", handle.widget))
        layout.addWidget(raster)
        layout.addWidget(gui.QLabel("QOpenGLWidget renderer", handle.widget))
        layout.addWidget(gl)

        def advance():
            state["phase"] = (state["phase"] + 1) % 100000
            raster.update()
            gl.update()

        ticker = timer(qt, handle, 50, advance)
        handle.controls.update(raster=raster, opengl=gl, timer=ticker, advance=advance)
        handle.inspect_ui = lambda: {"phase": state["phase"], "circles": 30}
        return handle
