# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/8e5aa13798c2763c.md
# this_file: ports/widgets/pyqt-official/scribble-8e5aa13798c2763c.py

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


def build(qt):
    sref = {}

    class Window(qt.QtGui.QWidget):
        def closeEvent(self, event):
            s = sref.get("s")
            if s is not None and s.state.get("modified"):
                event.ignore()
                s.controls["prompt"](
                    lambda: (s.state.update(modified=False), s.h.close())
                )
                return
            qt.QtGui.QWidget.closeEvent(self, event)

    with S.Session(qt, "Raster sketchpad", Window()) as s:
        sref["s"] = s
        s.vertical()
        image = [s.g.QImage(640, 420, s.g.QImage.Format_RGB32)]
        image[0].fill(s.g.QColor("white"))
        last = [None]
        s.state.update(modified=False, width=3, color="#275c8b")

        def paint(p, w, h):
            p.drawImage(s.c.QPoint(0, 0), image[0])

        def ensure(*args):
            w = max(image[0].width(), int(S.value(face, "width")))
            h = max(image[0].height(), int(S.value(face, "height")))
            if w == image[0].width() and h == image[0].height():
                return
            replacement = s.g.QImage(w, h, s.g.QImage.Format_RGB32)
            replacement.fill(s.g.QColor("white"))
            p = s.g.QPainter(replacement)
            try:
                p.drawImage(s.c.QPoint(0, 0), image[0])
            finally:
                p.end()
            image[0] = replacement

        def line(a, b):
            p = s.g.QPainter(image[0])
            try:
                p.setPen(
                    s.g.QPen(
                        s.g.QColor(s.state["color"]),
                        s.state["width"],
                        s.c.Qt.SolidLine,
                        s.c.Qt.RoundCap,
                        s.c.Qt.RoundJoin,
                    )
                )
                p.drawLine(a, b)
            finally:
                p.end()
            s.state["modified"] = True
            ax = int(S.value(a, "x"))
            ay = int(S.value(a, "y"))
            bx = int(S.value(b, "x"))
            by = int(S.value(b, "y"))
            radius = s.state["width"] + 2
            face.update(
                min(ax, bx) - radius,
                min(ay, by) - radius,
                abs(ax - bx) + 2 * radius,
                abs(ay - by) + 2 * radius,
            )

        def press(event):
            if event.button() == s.c.Qt.LeftButton:
                last[0] = event.pos()
                line(last[0], last[0])

        def move(event):
            if last[0] is not None and event.buttons() & s.c.Qt.LeftButton:
                line(last[0], event.pos())
                last[0] = event.pos()

        face = S.canvas(
            s,
            paint,
            {
                "press": press,
                "move": move,
                "release": lambda e: last.__setitem__(0, None),
                "resize": lambda e: ensure(),
            },
        )
        s.add(face)

        def save(path):
            suffix = Path(path).suffix.lstrip(".").upper() or "PNG"
            if not image[0].save(path, suffix):
                raise OSError("Cannot save this image")
            s.state["modified"] = False

        def prompt(then):
            if not s.state["modified"]:
                then()
                return
            dialog = s.keep("unsaved_dialog", s.alert(s.g.QMessageBox(s.window)))
            dialog.setText("Save the drawing before continuing?")
            dialog.setStandardButtons(
                s.g.QMessageBox.Save | s.g.QMessageBox.Discard | s.g.QMessageBox.Cancel
            )

            def response(button):
                standard = dialog.standardButton(button)
                if standard == s.g.QMessageBox.Discard:
                    s.state["modified"] = False
                    then()
                elif standard == s.g.QMessageBox.Save:
                    s.choose(lambda path: (save(path), then()), save=True)

            s.link(dialog, "buttonClicked(QAbstractButton*)", response)
            dialog.open()

        def load(path):
            replacement = s.g.QImage(path)
            if replacement.isNull():
                raise ValueError("Cannot read image")
            image[0] = replacement
            s.state["modified"] = False
            ensure()
            face.update()

        def clear():
            image[0].fill(s.g.QColor("white"))
            s.state["modified"] = True
            face.update()

        def color():
            dialog = s.keep("color_dialog", s.alert(s.g.QColorDialog(s.window)))
            s.link(
                dialog,
                "accepted()",
                lambda *a: s.state.update(color=str(dialog.selectedColor().name())),
            )
            dialog.open()

        def width():
            dialog = s.keep("width_dialog", s.alert(s.g.QInputDialog(s.window)))
            dialog.setInputMode(s.g.QInputDialog.IntInput)
            dialog.setIntRange(1, 50)
            dialog.setIntValue(s.state["width"])
            s.link(
                dialog,
                "accepted()",
                lambda *a: s.state.update(width=int(S.value(dialog, "intValue"))),
            )
            dialog.open()

        viewer = S.port("widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py")
        s.menu(
            "File",
            [
                ("Open", lambda: prompt(lambda: s.choose(load))),
                ("Save", lambda: s.choose(save, save=True)),
                ("Print", lambda: viewer.print_image(s, lambda: image[0])),
                ("Exit", lambda: prompt(s.h.close)),
            ],
        )
        s.menu(
            "Options", [("Pen color", color), ("Pen width", width), ("Clear", clear)]
        )
        s.menu(
            "Help",
            [
                (
                    "About",
                    lambda: s.state.update(help="Draw with the left mouse button."),
                )
            ],
        )
        s.keep("prompt", prompt)
        s.keep("load", load)
        s.keep("save", save)
        s.keep("clear", clear)
        return s.h
