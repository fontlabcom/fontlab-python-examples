#FLM: Proofs · Glyph Grid
# this_file: samples/proof_glyph_grid.py
"""Show the selected glyphs on every master side by side, drawn from their outlines.

Rows are glyphs, columns are masters; all cells share one scale so weights
and widths compare directly. The slider zooms. Composites are drawn with
their components in place. Nothing in the font changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Glyph Grid"
KEY = "proof_glyph_grid"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def selected_glyphs(package):
    """flGlyphs selected in the Font window, in font order; else the current glyph."""
    names = []
    try:
        import FL

        font = FL.fl.font
        names = [font[i].name for i in range(len(font)) if FL.fl.Selected(i)]
    except Exception:
        names = []
    if not names:
        glyph = fontlab.CurrentGlyph()
        names = [glyph.name] if glyph is not None else []
    glyphs = [package.findName(name) for name in names]
    return [g for g in glyphs if g is not None]


# ---------------------------------------------------------------- core
def layer_path(layer):
    """The layer's outline as one QPainterPath in font units (y up), components placed."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        transform = shape.transform
        for part in (shape.closedPath, shape.openedPath):
            if part is not None and not part.isEmpty():
                path.addPath(transform.map(part))
    return path


def metrics(package):
    """(descender, ascender) of the font; widened to the drawn outlines so accents fit."""
    return package.descender_value, package.ascender_value


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Grid(QtGui.QWidget):
    """Custom painter: one cell per glyph x master, baseline and advance box shown faintly."""

    LABEL = 18

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.paint_error = ""
        self.on_error = None  # dialog hook: show drawing errors in the status label
        self.cells = []  # [(glyph name, [(master, path, advance), ...])]
        self.masters = []
        self.frame = (-250, 750)
        self.cell = 120
        self.painted = 0

    def set_content(self, cells, masters, frame, cell):
        self.cells, self.masters, self.frame, self.cell = cells, masters, frame, cell
        width = self.LABEL * 5 + len(masters) * (cell + 8)
        height = self.LABEL + len(cells) * (cell + self.LABEL + 8) + 8
        self.setMinimumSize(width, height)
        self.resize(max(width, self.width), height)
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        try:
            self.draw(painter)
            self.paint_error = ""
        except Exception as error:  # an escaping exception with a live QPainter crashes FontLab
            self.paint_error = repr(error)
            if self.on_error is not None:
                self.on_error(self.paint_error)
        finally:
            painter.end()

    def draw(self, painter):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        text = QtGui.QColor(self.palette.color(QtGui.QPalette.Text))
        faint = QtGui.QColor(text)
        faint.setAlpha(40)
        soft = QtGui.QColor(text)
        soft.setAlpha(140)
        descender, ascender = self.frame
        scale = self.cell * 0.88 / float(max(1.0, ascender - descender))
        left = self.LABEL * 5
        painter.setPen(soft)
        for column, master in enumerate(self.masters):
            x = left + column * (self.cell + 8)
            painter.drawText(QtCore.QRectF(x, 0, self.cell, self.LABEL), int(QtCore.Qt.AlignCenter), master)
        self.painted = 0
        for row, (name, layers) in enumerate(self.cells):
            top = self.LABEL + row * (self.cell + self.LABEL + 8)
            painter.setPen(soft)
            painter.drawText(QtCore.QRectF(0, top, left - 8, self.cell),
                             int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), name)
            for column, (master, path, advance) in enumerate(layers):
                x = left + column * (self.cell + 8)
                painter.setPen(QtGui.QPen(QtGui.QBrush(faint), 1.0))
                painter.setBrush(QtGui.QBrush())
                painter.drawRoundedRect(QtCore.QRectF(x, top, self.cell, self.cell), 6, 6)
                if path is None:
                    painter.setPen(soft)
                    painter.drawText(QtCore.QRectF(x, top, self.cell, self.cell), int(QtCore.Qt.AlignCenter), "–")
                    continue
                offset = x + (self.cell - advance * scale) / 2.0
                baseline = top + self.cell * 0.06 + ascender * scale
                painter.drawLine(QtCore.QPointF(x + 4, baseline), QtCore.QPointF(x + self.cell - 4, baseline))
                painter.save()
                painter.translate(offset, baseline)
                painter.scale(scale, 0 - scale)
                painter.fillPath(path, QtGui.QBrush(text))
                painter.restore()
                painter.setPen(soft)
                painter.drawText(QtCore.QRectF(x, top + self.cell + 2, self.cell, self.LABEL),
                                 int(QtCore.Qt.AlignCenter), str(int(round(advance))))
                self.painted += 1


class GlyphGrid(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(560)
        self.resize(640, 560)
        self._connections = []
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []

        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)

        form = QtGui.QHBoxLayout()
        form.setSpacing(10)
        form.addWidget(QtGui.QLabel("Zoom"))
        self.zoom = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.zoom.setRange(48, 240)
        self.zoom.setValue(110)
        form.addWidget(self.zoom, 1)
        self.zoom_label = QtGui.QLabel()
        self.zoom_label.setMinimumWidth(48)
        form.addWidget(self.zoom_label)
        root.addLayout(form)

        self.grid = Grid()
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setWidget(self.grid)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setFrameShape(QtGui.QFrame.NoFrame)
        root.addWidget(self.scroll_area, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.grid.on_error = lambda text: self.status.setText("Drawing failed: " + text)
        self.reload_button = QtGui.QPushButton("Reload selection")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self._connect(self.zoom.valueChanged, lambda *a: self.refresh())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal, slot):
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:  # an exception escaping a PythonQt slot can take FontLab down
                self.slot_error = repr(error)
                label = getattr(self, "status", None)
                if label is not None:
                    label.setText("Error: " + self.slot_error)
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def reload(self):
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.refresh()

    def refresh(self):
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then click Reload selection.")
        else:
            self.subtitle.setText(f"{count} glyph{'s' if count != 1 else ''} × {len(self.masters)} masters, "
                                  "one scale for all cells; numbers are advance widths.")
        cells = []
        for glyph in self.glyphs:
            row = []
            for master in self.masters:
                layer = glyph.findLayer(master)
                if layer is None or layer.isNull:
                    row.append((master, None, 0))
                else:
                    row.append((master, layer_path(layer), layer.advanceWidth))
            cells.append((glyph.name, row))
        frame = metrics(self.package) if self.package else (-250, 750)
        for _, row in cells:
            for _, path, _ in row:
                if path is not None and not path.isEmpty():
                    box = path.boundingRect()
                    frame = (min(frame[0], box.top()), max(frame[1], box.bottom()))
        self.grid.set_content(cells, self.masters, frame, self.zoom.value)
        self.zoom_label.setText(f"{self.zoom.value} px")
        self.status.setText(f"{count * len(self.masters)} cells")

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        getattr(sys, "_fontlab_samples", {}).pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = GlyphGrid(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
