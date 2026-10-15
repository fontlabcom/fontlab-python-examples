# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/0788354954c8e613.md
# this_file: ports/threads/pyqt-official/mandelbrot-0788354954c8e613.py

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


import colorsys
import queue
import threading


def scanline(width, height, row, center, scale, limit):
    result = []
    imaginary = center[1] + (row - height / 2) * scale
    for column in range(width):
        c = complex(center[0] + (column - width / 2) * scale, imaginary)
        z, count = 0j, 0
        while abs(z) <= 2 and count < limit:
            z = z * z + c
            count += 1
        result.append(0 if count == limit else 1 + count % 511)
    return result


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Fractal explorer") as (handle, layout):
        state = {
            "center": [-0.5, 0.0],
            "scale": 0.008,
            "generation": 0,
            "pending": True,
            "thread": None,
            "cancel": threading.Event(),
            "image": None,
            "drag": None,
            "pass": 0,
        }
        results = queue.Queue(8)
        spectrum = []
        for index in range(512):
            r, g, b = colorsys.hsv_to_rgb(index / 512, 0.8, 0.95)
            spectrum.append(gui.QColor(int(r * 255), int(g * 255), int(b * 255)).rgb())
        spectrum[0] = gui.QColor("black").rgb()

        def request():
            state["generation"] += 1
            state["cancel"].set()
            state["pending"] = True

        class Canvas(gui.QWidget):
            def paintEvent(self, event):
                painter = gui.QPainter(self)
                try:
                    if state["image"] is not None:
                        painter.drawImage(self.rect(), state["image"])
                finally:
                    painter.end()

            def wheelEvent(self, event):
                delta = event.angleDelta()
                state["scale"] *= 0.8 if value(delta, "y") > 0 else 1.25
                request()
                event.accept()

            def keyPressEvent(self, event):
                key = event.key()
                if key in (core.Qt.Key_Plus, core.Qt.Key_Equal, core.Qt.Key_Minus):
                    state["scale"] *= 1.25 if key == core.Qt.Key_Minus else 0.8
                elif key in (
                    core.Qt.Key_Left,
                    core.Qt.Key_Right,
                    core.Qt.Key_Up,
                    core.Qt.Key_Down,
                ):
                    axis = 0 if key in (core.Qt.Key_Left, core.Qt.Key_Right) else 1
                    direction = -1 if key in (core.Qt.Key_Left, core.Qt.Key_Up) else 1
                    state["center"][axis] += direction * state["scale"] * 40
                else:
                    gui.QWidget.keyPressEvent(self, event)
                    return
                request()
                event.accept()

            def mousePressEvent(self, event):
                point = event.pos()
                state["drag"] = (value(point, "x"), value(point, "y"))

            def mouseReleaseEvent(self, event):
                if state["drag"] is not None:
                    point = event.pos()
                    for axis, name in enumerate(("x", "y")):
                        state["center"][axis] -= (
                            value(point, name) - state["drag"][axis]
                        ) * state["scale"]
                    state["drag"] = None
                    request()

            def resizeEvent(self, event):
                gui.QWidget.resizeEvent(self, event)
                request()

        canvas = Canvas(handle.widget)
        canvas.setFocusPolicy(core.Qt.StrongFocus)
        layout.addWidget(canvas)
        layout.addWidget(
            gui.QLabel(
                "Wheel or +/− zooms; arrows and a drag move the view.", handle.widget
            )
        )

        def stop():
            state["cancel"].set()
            worker = state["thread"]
            if worker is not None:
                worker.join(1)
                if worker.is_alive():
                    raise RuntimeError("Owned fractal worker did not stop")

        def poll():
            if state["pending"]:
                worker = state["thread"]
                if worker is not None and worker.is_alive():
                    return
                width = min(512, max(32, int(value(canvas, "width"))))
                height = min(320, max(32, int(value(canvas, "height"))))
                generation, center, scale = (
                    state["generation"],
                    tuple(state["center"]),
                    state["scale"],
                )
                cancel = threading.Event()
                state.update(cancel=cancel, pending=False)
                state["image"] = gui.QImage(width, height, gui.QImage.Format_RGB32)
                state["image"].fill(0)

                def render():
                    for refinement in range(8):
                        for row in range(height):
                            if cancel.is_set():
                                return
                            pixels = scanline(
                                width, height, row, center, scale, 24 * (refinement + 1)
                            )
                            while not cancel.is_set():
                                try:
                                    results.put(
                                        (generation, refinement + 1, row, pixels),
                                        timeout=0.02,
                                    )
                                    break
                                except queue.Full:
                                    pass

                worker = threading.Thread(target=render, name="example-fractal")
                state["thread"] = worker
                worker.start()
            for _ in range(4):
                try:
                    generation, refinement, row, pixels = results.get_nowait()
                except queue.Empty:
                    break
                if generation != state["generation"]:
                    continue
                for column, color in enumerate(pixels):
                    state["image"].setPixel(column, row, spectrum[color])
                state["pass"] = refinement
                canvas.update()

        handle.cleanup.append(stop)
        ticker = timer(qt, handle, 20, poll)
        handle.controls.update(canvas=canvas, request=request, poll=poll, timer=ticker)
        handle.inspect_ui = lambda: {
            "center": list(state["center"]),
            "scale": state["scale"],
            "generation": state["generation"],
            "pass": state["pass"],
            "running": bool(state["thread"] and state["thread"].is_alive()),
        }
        return handle
