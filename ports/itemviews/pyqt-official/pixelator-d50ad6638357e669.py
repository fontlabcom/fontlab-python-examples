# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/d50ad6638357e669.md
# this_file: ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py

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


def brightness(pixel):
    pixel = int(pixel)
    return (
        ((pixel >> 16) & 255) * 11 + ((pixel >> 8) & 255) * 16 + (pixel & 255) * 5
    ) // 32


def dot_diameter(brightness, size):
    return max(
        0.0, min(float(size), float(size) * (255 - max(0, min(255, brightness))) / 255)
    )


def build(qt):
    with S.Session(qt, "Grayscale dot rendering") as s:
        s.vertical()
        image = [s.g.QImage(24, 18, s.g.QImage.Format_RGB32)]
        image[0].fill(s.g.QColor("white"))
        for y in range(18):
            for x in range(24):
                gray = x * 255 // 23
                image[0].setPixel(x, y, 0xFF000000 | (gray << 16) | (gray << 8) | gray)
        size = s.spin("pixel_size", 4, 32, 12)
        c = s.c

        class Pixels(s.g.QAbstractTableModel):
            def rowCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                return 0 if parent.isValid() else image[0].height()

            def columnCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                return 0 if parent.isValid() else image[0].width()

            def data(self, index, role=c.Qt.DisplayRole):
                if index.isValid() and role in [c.Qt.DisplayRole, c.Qt.EditRole]:
                    return brightness(image[0].pixel(index.column(), index.row()))
                return None

        model = s.keep("model", Pixels(s.window))
        s.h.model = model
        view = s.view("view", model)
        view.horizontalHeader().hide()
        view.verticalHeader().hide()
        view.setShowGrid(False)

        class Dots(s.g.QStyledItemDelegate):
            def paint(self, p, option, index):
                rect = option.rect
                w = int(S.value(rect, "width"))
                h = int(S.value(rect, "height"))
                diameter = dot_diameter(int(model.data(index)), min(w, h))
                x = float(S.value(rect, "x")) + (w - diameter) / 2
                y = float(S.value(rect, "y")) + (h - diameter) / 2
                p.save()
                try:
                    selected = bool(option.state & s.g.QStyle.State_Selected)
                    if selected:
                        p.fillRect(rect, option.palette.highlight())
                    p.setBrush(
                        option.palette.highlightedText()
                        if selected
                        else s.g.QBrush(s.g.QColor("black"))
                    )
                    p.setPen(c.Qt.NoPen)
                    p.drawEllipse(c.QRectF(x, y, diameter, diameter))
                finally:
                    p.restore()

        delegate = s.keep("delegate", Dots(view))
        view.setItemDelegate(delegate)

        def resize(n):
            view.horizontalHeader().setDefaultSectionSize(n)
            view.verticalHeader().setDefaultSectionSize(n)

        s.link(size, "valueChanged(int)", resize)
        resize(12)

        def load(path):
            replacement = s.g.QImage(path)
            if replacement.isNull():
                raise ValueError("Unsupported image")

            def commit():
                model.beginResetModel()
                image[0] = replacement.convertToFormat(s.g.QImage.Format_Grayscale8)
                model.endResetModel()
                s.state["dimensions"] = [replacement.width(), replacement.height()]

            if replacement.width() * replacement.height() > 90000:
                dialog = s.keep("large_dialog", s.alert(s.g.QMessageBox(s.window)))
                dialog.setText("This image creates many cells. Continue?")
                dialog.setStandardButtons(s.g.QMessageBox.Ok | s.g.QMessageBox.Cancel)
                s.link(dialog, "accepted()", lambda *a: commit())
                dialog.open()
            else:
                commit()

        def printing():
            printer = s.keep("printer", s.g.QPrinter())
            dialog = s.keep(
                "print_dialog", s.alert(s.g.QPrintDialog(printer, s.window))
            )

            def accepted(*args):
                painter = s.g.QPainter(printer)
                row = [0]
                progress = s.keep(
                    "print_progress", s.alert(s.g.QProgressDialog(s.window))
                )
                progress.setRange(0, image[0].height())
                progress.open()
                ended = [False]

                def end():
                    timer.stop()
                    if not ended[0]:
                        painter.end()
                        ended[0] = True
                    progress.hide()

                def step():
                    for y in range(row[0], min(image[0].height(), row[0] + 8)):
                        for x in range(image[0].width()):
                            d = dot_diameter(brightness(image[0].pixel(x, y)), 8)
                            painter.setBrush(s.g.QColor("black"))
                            painter.drawEllipse(
                                c.QRectF(x * 8 + (8 - d) / 2, y * 8 + (8 - d) / 2, d, d)
                            )
                    row[0] += 8
                    progress.setValue(min(row[0], image[0].height()))
                    if row[0] >= image[0].height():
                        end()

                timer = s.timer("print_timer", 0, step)
                s.link(progress, "canceled()", lambda *a: end())
                s.h.cleanup.insert(0, end)

            s.link(dialog, "accepted()", accepted)
            dialog.open()

        s.menu(
            "File",
            [
                ("Open", lambda: s.choose(load)),
                ("Print", printing),
                ("Exit", s.h.close),
            ],
        )
        s.menu(
            "Help",
            [("About", lambda: s.state.update(help="Darker pixels make larger dots."))],
        )
        s.keep("load", load)
        return s.h
