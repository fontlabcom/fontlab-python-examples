#FLM: Kerning · Text Preview
# this_file: samples/kerning_text_preview.py
"""Set text from the font's outlines with its kerning applied, per master, at any size.

Type text or /glyphname tokens, pick a master and drag the size slider; lines wrap to the
window. Kerned gaps can be labelled with their values, and kerning can be switched off to see
the raw spacing. FontLab resolves each pair, including class kerning. Nothing is edited.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Kerning Text Preview"
KEY = "kerning_text_preview"
DEFAULT_TEXT = "AVATAR LTAVA Tyre WAVE /Aacute/V"
MARGIN = 18


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


def pair_value(kerning, left, right):
    """Kerning FontLab applies between two glyphs (class pairs included); 0 when none."""
    try:
        value = kerning.get((left, right))
    except Exception:
        value = None
    return value or 0


def layout(package, names, master, kerned=True):
    """[(name, x, advance, kern before this glyph)] in font units along one line."""
    kerning = package.kerning(master)
    rows, x, previous = [], 0, None
    for name in names:
        layer = package.findName(name).findLayer(master)
        if layer is None or layer.isNull:
            continue
        kern = pair_value(kerning, previous, name) if kerned and previous is not None else 0
        x += kern
        rows.append((name, x, layer.advanceWidth, kern))
        x += layer.advanceWidth
        previous = name
    return rows


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Canvas(QtGui.QWidget):
    """Paints the laid-out glyphs at the chosen size, wrapping lines to the widget width."""

    def __init__(self, owner):
        QtGui.QWidget.__init__(self)
        self.paint_error = None
        self.owner = owner
        self.setMinimumSize(560, 260)

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
        scale = owner.size_slider.value / owner.upm
        values = owner.show_values.isChecked()
        line_height = (owner.ascender - owner.descender) * scale * 1.15 + (20 if values else 0)
        ink = QtGui.QColor(palette.color(QtGui.QPalette.WindowText))
        accent = QtGui.QColor(palette.color(QtGui.QPalette.Link))
        small = painter.font()
        small.setPointSizeF(max(small.pointSizeF() * 0.8, 8))
        painter.setFont(small)
        usable = self.width - 2 * MARGIN
        origin, line = 0, 0
        for name, x, advance, kern in rows:
            if (x + advance - origin) * scale > usable and x > origin:
                origin, line = x, line + 1
            baseline = MARGIN + owner.ascender * scale + line * line_height
            if baseline - owner.ascender * scale > self.height:
                break
            left = MARGIN + (x - origin) * scale
            if kern and values:
                painter.setPen(accent)
                painter.drawText(QtCore.QRectF(left - 20, baseline - owner.descender * scale + 2, 40, 16), int(QtCore.Qt.AlignCenter), f"{kern:g}")
            painter.save()
            painter.translate(left, baseline)
            painter.scale(scale, -scale)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(ink))
            painter.drawPath(owner.path(name))
            painter.restore()


class TextPreview(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(680)
        self.resize(760, 520)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.upm = self.package.upm if self.package else 1000
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
        self.text.setPlaceholderText("Text, or /glyphname tokens")
        self.master = QtGui.QComboBox()
        for name in self.masters:
            self.master.addItem(name)
        if self.current_master in self.masters:
            self.master.setCurrentIndex(self.masters.index(self.current_master))
        self.size_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setRange(16, 240)
        self.size_slider.setValue(72)
        self.size_label = QtGui.QLabel()
        self.kerned = QtGui.QCheckBox("Kerning")
        self.kerned.setChecked(True)
        self.show_values = QtGui.QCheckBox("Show values")
        self.show_values.setChecked(True)
        form.addWidget(QtGui.QLabel("Text"), 0, 0)
        form.addWidget(self.text, 0, 1, 1, 4)
        form.addWidget(QtGui.QLabel("Master"), 1, 0)
        form.addWidget(self.master, 1, 1)
        form.addWidget(self.kerned, 1, 2)
        form.addWidget(self.show_values, 1, 3)
        form.addWidget(QtGui.QLabel("Size"), 2, 0)
        form.addWidget(self.size_slider, 2, 1, 1, 3)
        form.addWidget(self.size_label, 2, 4)
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
        self._connect(self.kerned.toggled, lambda *a: self.refresh())
        self._connect(self.show_values.toggled, lambda *a: self.canvas.update())
        self._connect(self.size_slider.valueChanged, lambda *a: self.resized())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.resized()
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
        return "Open a font first." if self.package is None else "Type some text above."

    def resized(self):
        self.size_label.setText(f"{self.size_slider.value} px")
        self.canvas.update()

    def refresh(self):
        if self.package is None:
            self.rows = []
            self.subtitle.setText("Open a font first.")
        else:
            names = parse_text(self.text.text, self.package)
            self.rows = layout(self.package, names, self.chosen_master(), self.kerned.isChecked())
            self.subtitle.setText(f"{self.chosen_master()} master · glyph outlines with "
                                  f"{'kerning applied' if self.kerned.isChecked() else 'kerning off'}")
        kerned = [r for r in self.rows if r[3]]
        total = sum(r[3] for r in kerned)
        self.status.setText(f"{len(self.rows)} glyphs · {len(kerned)} kerned gaps, {total:g} units in total")
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
    dialog = TextPreview(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
