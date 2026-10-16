#FLM: Proofs · Waterfall
# this_file: samples/proof_waterfall.py
"""Render a line of text in a cascade of sizes, drawn straight from the glyph outlines.

Type any text (use /glyphname for unencoded glyphs, e.g. /a.ss01), pick a
master and edit the list of pixel sizes. Characters the font lacks show as
red boxes. Advance widths only: kerning is not applied. Nothing in the font
changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Waterfall"
KEY = "proof_waterfall"
DEFAULT_TEXT = "Hamburgefonstiv 0123"
DEFAULT_SIZES = "10 12 14 18 24 32 48 64 96"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def character_map():
    """{code point: glyph name} of the current font (first glyph wins)."""
    font = fontlab.CurrentFont()
    out = {}
    for glyph in (font.glyphs if font is not None else []):
        for code in glyph.unicodes:
            out.setdefault(code, glyph.name)
    return out


def layer_path(layer):
    """The layer's outline as one QPainterPath in font units (y up), components placed."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        for part in (shape.closedPath, shape.openedPath):
            if part is not None and not part.isEmpty():
                path.addPath(shape.transform.map(part))
    return path


# ---------------------------------------------------------------- core
def parse_text(text, cmap, names):
    """[glyph name or None] for the text; '/name ' or '/name/' addresses glyphs by name."""
    out, i = [], 0
    while i < len(text):
        char = text[i]
        if char == "/" and i + 1 < len(text) and text[i + 1] not in " /":
            end = i + 1
            while end < len(text) and text[end] not in " /":
                end += 1
            name = text[i + 1:end]
            out.append(name if name in names else None)
            i = end + 1 if end < len(text) and text[end] == " " else end
            continue
        out.append(cmap.get(ord(char)))
        i += 1
    return out


def parse_sizes(text):
    sizes = []
    for part in text.replace(",", " ").split():
        try:
            size = float(part)
        except ValueError:
            continue
        if 4 <= size <= 400:
            sizes.append(size)
    return sizes


def glyph_run(package, glyph_names, master):
    """[(path or None, advance)] in font units for one master; None marks a missing glyph."""
    cache, out = {}, []
    for name in glyph_names:
        if name is None:
            out.append((None, package.upm * 0.5))
            continue
        if name not in cache:
            glyph = package.findName(name)
            layer = glyph.findLayer(master) if glyph is not None else None
            cache[name] = (layer_path(layer), layer.advanceWidth) if layer is not None else (None, package.upm * 0.5)
        out.append(cache[name])
    return out


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class WaterfallView(QtGui.QWidget):
    """Custom painter: one line per size, glyphs filled with the palette's text colour."""

    GUTTER = 44

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.paint_error = ""
        self.on_error = None  # dialog hook: show drawing errors in the status label
        self.run, self.sizes, self.upm, self.ascender = [], [], 1000.0, 800.0
        self.width_units = 0

    def set_content(self, glyphs, sizes, upm, ascender):
        self.run, self.sizes, self.upm, self.ascender = glyphs, sizes, float(upm), float(ascender)
        self.width_units = sum(advance for _, advance in glyphs)
        height = int(sum(size * 1.3 + 8 for size in sizes)) + 16
        width = int(self.GUTTER + max([self.width_units * s / self.upm for s in sizes] or [0])) + 24
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
        soft = QtGui.QColor(text)
        soft.setAlpha(120)
        alert = QtGui.QColor("#d33")
        brush = QtGui.QBrush(text)
        y = 8.0
        for size in self.sizes:
            scale = size / self.upm
            baseline = y + self.ascender * scale * 1.05
            painter.setPen(soft)
            painter.drawText(QtCore.QRectF(0, baseline - 14, self.GUTTER - 10, 16),
                             int(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom), f"{size:g}")
            x = float(self.GUTTER)
            for path, advance in self.run:
                if path is None:
                    painter.setPen(QtGui.QPen(QtGui.QBrush(alert), 1.0))
                    painter.setBrush(QtGui.QBrush())
                    painter.drawRect(QtCore.QRectF(x + 1, baseline - size * 0.7, advance * scale - 2, size * 0.7))
                else:
                    painter.save()
                    painter.translate(x, baseline)
                    painter.scale(scale, 0 - scale)
                    painter.fillPath(path, brush)
                    painter.restore()
                x += advance * scale
            y += size * 1.3 + 8


class Waterfall(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(620)
        self.resize(760, 600)
        self._connections = []
        self.package = current_package()
        self.cmap = character_map()
        self.names = set(self.cmap.values())
        font = fontlab.CurrentFont()
        if font is not None:
            self.names = {g.name for g in font.glyphs}

        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        title_font = heading.font
        title_font.setPointSizeF(title_font.pointSizeF() * 1.35)
        title_font.setBold(True)
        heading.setFont(title_font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.text = QtGui.QLineEdit(DEFAULT_TEXT)
        self.sizes = QtGui.QLineEdit(DEFAULT_SIZES)
        self.master = QtGui.QComboBox()
        masters = list(self.package.masters) if self.package else []
        for name in masters:
            self.master.addItem(name)
        if self.package and self.package.master in masters:
            self.master.setCurrentIndex(masters.index(self.package.master))
        form.addWidget(QtGui.QLabel("Text"), 0, 0)
        form.addWidget(self.text, 0, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Sizes (px)"), 1, 0)
        form.addWidget(self.sizes, 1, 1)
        form.addWidget(QtGui.QLabel("Master"), 1, 2)
        form.addWidget(self.master, 1, 3)
        form.setColumnStretch(1, 2)
        form.setColumnStretch(3, 1)
        root.addLayout(form)

        self.view = WaterfallView()
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setWidget(self.view)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # long lines clip at the edge
        self.scroll_area.setFrameShape(QtGui.QFrame.NoFrame)
        self.scroll_area.setBackgroundRole(QtGui.QPalette.Base)
        self.scroll_area.setAutoFillBackground(True)
        root.addWidget(self.scroll_area, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.view.on_error = lambda text: self.status.setText("Drawing failed: " + text)
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        for line in (self.text, self.sizes):
            self._connect(line.textChanged, lambda *a: self.refresh())
        self._connect(self.master.currentIndexChanged, lambda *a: self.refresh())
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

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        master = self.master.currentText
        master = master() if callable(master) else master
        self.glyph_names = parse_text(self.text.text, self.cmap, self.names)
        missing = sum(1 for n in self.glyph_names if n is None)
        glyphs = glyph_run(self.package, self.glyph_names, master)
        size_list = parse_sizes(self.sizes.text)
        self.view.set_content(glyphs, size_list, self.package.upm, self.package.ascender_value)
        self.subtitle.setText(f"Master {master} · {len(self.glyph_names)} glyphs · advance widths, no kerning. "
                              "Use /name for unencoded glyphs.")
        note = f" · {missing} missing (red boxes)" if missing else ""
        self.status.setText(f"Line width {self.view.width_units:g} units · {len(size_list)} sizes{note}")

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
    dialog = Waterfall(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
