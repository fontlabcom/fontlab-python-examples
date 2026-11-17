# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c82d1af7d1a7b0cf.md
# this_file: Scripts/OpenGL/Raster And OpenGL Painting.py
"""Compare the same animated QPainter scene on raster and OpenGL surfaces."""
from contextlib import contextmanager
from fontlab_python_lessons import qt_demos as S
from fontlab_python_lessons.qt_demos import value


@contextmanager
def owned(qt, title):
    with S.Session(qt, title) as session:
        session.vertical()
        yield session.h, session.layout


def timer(qt, handle, interval, callback):
    item = qt.QtCore.QTimer(handle.widget)
    handle.connect_old(item, "timeout()", lambda: callback())
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
            except Exception as error:
                print("Painting failed:", error)
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


def main():
    return S.launch(build, "restored_c82d1af7d1a7b0cf", "Raster And OpenGL Painting")


if __name__ == "__main__":
    main()
