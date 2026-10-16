#FLM: Metrics · Spacing String Preview
# this_file: samples/metrics_spacing_string_preview.py
"""Render a spacing control string such as HOHnono from the font's own outlines and advances.

Type characters or /glyphname tokens, pick a master, and judge the rhythm of straight and round
sidebearings without generating a font. Advance boxes and LSB/RSB numbers can be shown under
each glyph. Nothing is edited; the preview follows the outlines as they are now.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Spacing String Preview"
KEY = "metrics_spacing_string_preview"
DEFAULT_TEXT = "HHOHOOH nnonoon"
MARGIN = 24


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


# ---------------------------------------------------------------- core
def parse_text(text, package):
    """Glyph names for the text: characters by Unicode, '/name' tokens by name (ended by space or '/')."""
    names, i = [], 0
    while i < len(text):
        char = text[i]
        if char == "/":
            j = i + 1
            while j < len(text) and text[j] not in " /":
                j += 1
            token = text[i + 1:j]
            if token and package.findName(token) is not None:
                names.append(token)
            i = j + (1 if j < len(text) and text[j] == " " else 0)
            continue
        glyph = package.findUnicode(ord(char))
        if glyph is not None:
            names.append(glyph.name)
        i += 1
    return names


def outline(layer):
    """The layer's outline as one QPainterPath, components placed by their transforms."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        part = QtGui.QPainterPath()
        for contour in shape.getContours():
            part.addPath(contour.path())
        path.addPath(shape.transform.map(part))
    return path


def layout(package, names, master):
    """[(name, x, advance, lsb, rsb)]: pen positions along the line, in font units."""
    rows, x = [], 0
    for name in names:
        layer = package.findName(name).findLayer(master)
        if layer is None or layer.isNull:
            continue
        advance = layer.advanceWidth
        box = layer.boundingBox
        empty = box.width() <= 0 and box.height() <= 0
        lsb = None if empty else box.x()
        rsb = None if empty else advance - box.x() - box.width()
        rows.append((name, x, advance, lsb, rsb))
        x += advance
    return rows


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Canvas(QtGui.QWidget):
    """Paints one line of glyphs, scaled to fit, with optional boxes and sidebearing numbers."""

    def __init__(self, owner):
        QtGui.QWidget.__init__(self)
        self.paint_error = None
        self.owner = owner
        self.setMinimumSize(560, 240)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        try:
            self.draw(painter)
            self.paint_error = None
        except Exception as error:  # an escaping error here can crash FontLab
            self.paint_error = repr(error)
        finally:
            painter.end()

    def draw(self, painter):
        owner = self.owner
        palette = self.palette
        painter.fillRect(self.rect, palette.color(QtGui.QPalette.Base))
        rows = owner.rows
        if not rows:
            painter.setPen(QtGui.QColor(muted(self)))
            painter.drawText(self.rect, int(QtCore.Qt.AlignCenter), owner.empty_message())
            return
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        total = rows[-1][1] + rows[-1][2]
        top, bottom = owner.ascender, owner.descender
        labels = 44 if owner.show_numbers.isChecked() else 8
        scale = min((self.width - 2 * MARGIN) / max(total, 1), (self.height - 2 * MARGIN - labels) / max(top - bottom, 1))
        left = (self.width - total * scale) / 2
        spare = self.height - 2 * MARGIN - labels - (top - bottom) * scale
        baseline = MARGIN + max(spare, 0) / 2 + top * scale
        guide = QtGui.QColor(palette.color(QtGui.QPalette.Mid))
        accent = QtGui.QColor(palette.color(QtGui.QPalette.Link))
        ink = QtGui.QColor(palette.color(QtGui.QPalette.WindowText))
        box = QtGui.QColor(guide)
        box.setAlpha(90)
        small = painter.font()
        small.setPointSizeF(max(small.pointSizeF() * 0.85, 8))
        painter.setFont(small)
        painter.setPen(QtGui.QPen(QtGui.QBrush(guide), 1.0))
        painter.drawLine(QtCore.QPointF(left, baseline), QtCore.QPointF(left + total * scale, baseline))
        for name, x, advance, lsb, rsb in rows:
            x0 = left + x * scale
            if owner.show_boxes.isChecked():
                painter.setPen(QtGui.QPen(QtGui.QBrush(box), 1.0))
                painter.drawRect(QtCore.QRectF(x0, baseline - top * scale, advance * scale, (top - bottom) * scale))
            painter.save()
            painter.translate(x0, baseline)
            painter.scale(scale, -scale)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(ink))
            painter.drawPath(owner.path(name))
            painter.restore()
            if owner.show_numbers.isChecked() and lsb is not None:
                painter.setPen(accent)
                # LSB on the first row, RSB on the second, so neighbouring numbers never touch.
                y = baseline - bottom * scale + 6
                cell = QtCore.QRectF(x0 + 2, y, advance * scale - 4, 16)
                painter.drawText(cell, int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop), f"{round(lsb)}")
                painter.drawText(cell.translated(0, 17), int(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop), f"{round(rsb)}")


class SpacingPreview(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(640)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.ascender = self.package.ascender_value if self.package else 800
        self.descender = self.package.descender_value if self.package else -200
        self.rows = []
        self.paths = {}
        self._connections = []

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

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.text = QtGui.QLineEdit(DEFAULT_TEXT)
        self.text.setPlaceholderText("Characters, or /glyphname tokens")
        self.master = QtGui.QComboBox()
        for name in self.masters:
            self.master.addItem(name)
        if self.current_master in self.masters:
            self.master.setCurrentIndex(self.masters.index(self.current_master))
        self.show_boxes = QtGui.QCheckBox("Advance boxes")
        self.show_boxes.setChecked(True)
        self.show_numbers = QtGui.QCheckBox("LSB / RSB numbers")
        self.show_numbers.setChecked(True)
        form.addWidget(QtGui.QLabel("Text"), 0, 0)
        form.addWidget(self.text, 0, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Master"), 1, 0)
        form.addWidget(self.master, 1, 1)
        form.addWidget(self.show_boxes, 1, 2)
        form.addWidget(self.show_numbers, 1, 3)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.canvas = Canvas(self)
        root.addWidget(self.canvas, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setDefault(True)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self._connect(self.text.textChanged, lambda *a: self.refresh())
        self._connect(self.master.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.show_boxes.toggled, lambda *a: self.canvas.update())
        self._connect(self.show_numbers.toggled, lambda *a: self.canvas.update())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal, slot):
        def guarded(*args):
            # An exception escaping a PythonQt slot can take FontLab down: report it instead.
            try:
                return slot(*args)
            except Exception as error:
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def chosen_master(self):
        return self.masters[self.master.currentIndex] if self.masters else ""

    def path(self, name):
        key = (name, self.chosen_master())
        if key not in self.paths:
            self.paths[key] = outline(self.package.findName(name).findLayer(key[1]))
        return self.paths[key]

    def empty_message(self):
        if self.package is None:
            return "Open a font first."
        return "Type characters or /glyphname tokens above."

    def refresh(self):
        if self.package is None:
            self.rows = []
            self.subtitle.setText("Open a font first.")
        else:
            names = parse_text(self.text.text, self.package)
            self.rows = layout(self.package, names, self.chosen_master())
            self.subtitle.setText(f"{self.chosen_master()} master · {len(names)} glyphs drawn from their outlines and advances, no kerning")
        width = self.rows[-1][1] + self.rows[-1][2] if self.rows else 0
        self.status.setText(f"{len(self.rows)} glyphs · line width {width:g} units")
        self.canvas.update()

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        self.paths = {}
        getattr(sys, "_fontlab_samples", {}).pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = SpacingPreview(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
