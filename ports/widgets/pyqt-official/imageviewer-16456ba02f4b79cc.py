# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/16456ba02f4b79cc.md
# this_file: ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py

import importlib.util
import sys
from pathlib import Path

_key = "fontlab_cleanroom_a_primitives"
if _key not in sys.modules:
    _path = (
        Path(__file__).resolve().parents[2]
        / "layouts/pyqt-official/basiclayouts-2f94fe07de765888.py"
    )
    _spec = importlib.util.spec_from_file_location(_key, _path)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_key] = _module
    try:
        _spec.loader.exec_module(_module)
    except BaseException:
        sys.modules.pop(_key, None)
        raise
S = sys.modules[_key]


def generated_image(qt, width=160, height=120):
    image = qt.QtGui.QImage(width, height, qt.QtGui.QImage.Format_RGB32)
    image.fill(qt.QtGui.QColor("#f0e5c8"))
    painter = qt.QtGui.QPainter(image)
    try:
        painter.setBrush(qt.QtGui.QColor("#407eaa"))
        painter.drawEllipse(20, 15, 80, 80)
        painter.setBrush(qt.QtGui.QColor("#ad6851"))
        painter.drawRect(80, 55, 60, 45)
    finally:
        painter.end()
    return image


def print_image(s, image):
    printer = s.keep("printer", s.g.QPrinter())
    dialog = s.keep("print_dialog", s.alert(s.g.QPrintDialog(printer, s.window)))

    def accepted(*args):
        painter = s.g.QPainter(printer)
        try:
            painter.drawImage(s.c.QPoint(0, 0), image())
        finally:
            painter.end()

    s.link(dialog, "accepted()", accepted)
    dialog.open()


def build(qt):
    with S.Session(qt, "Image viewer") as s:
        s.vertical()
        label = s.keep("image", s.g.QLabel(s.window))
        scroll = s.keep("scroll", s.g.QScrollArea(s.window))
        scroll.setWidget(label)
        s.add(scroll)
        image = [None]
        scale = [1.0]
        fit = [False]

        def show():
            if image[0] is None:
                return
            label.setPixmap(s.g.QPixmap.fromImage(image[0]))
            label.setScaledContents(True)
            if not fit[0]:
                label.resize(
                    int(image[0].width() * scale[0]), int(image[0].height() * scale[0])
                )
            s.state.update(scale=scale[0], fit=fit[0], loaded=True)

        def load(path):
            replacement = s.g.QImage(path)
            if replacement.isNull():
                s.state["error"] = "Cannot read this image"
                return False
            image[0] = replacement
            scale[0] = 1.0
            show()
            enable()
            return True

        def zoom(factor):
            if image[0] is None or fit[0]:
                return
            scale[0] *= factor
            show()
            for bar in [scroll.horizontalScrollBar(), scroll.verticalScrollBar()]:
                bar.setValue(
                    int(
                        factor * int(S.value(bar, "value"))
                        + (factor - 1) * int(S.value(bar, "pageStep")) / 2
                    )
                )

        def normal():
            if image[0] is not None:
                scale[0] = 1.0
                show()

        def fit_window():
            fit[0] = not fit[0]
            scroll.setWidgetResizable(fit[0])
            show()
            enable()

        s.menu(
            "File",
            [
                ("Open", lambda: s.choose(load)),
                (
                    "Print",
                    lambda: (
                        print_image(s, lambda: image[0])
                        if image[0] is not None
                        else None
                    ),
                ),
                ("Exit", s.h.close),
            ],
        )
        s.menu(
            "View",
            [
                ("Zoom in", lambda: zoom(1.25)),
                ("Zoom out", lambda: zoom(0.8)),
                ("Normal", normal),
                ("Fit", fit_window),
            ],
        )
        s.menu(
            "Help",
            [
                (
                    "About",
                    lambda: s.state.update(help="Open an image to explore its pixels."),
                )
            ],
        )

        def enable():
            for key in ["Zoom in", "Zoom out", "Normal"]:
                s.controls["action_" + key].setEnabled(
                    image[0] is not None and not fit[0]
                )
            for key in ["Print", "Fit"]:
                s.controls["action_" + key].setEnabled(image[0] is not None)

        s.state.update(loaded=False, fit=False, scale=1.0)
        enable()
        s.keep("load", load)
        s.keep("zoom", zoom)
        return s.h
