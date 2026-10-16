#FLM: Proofs · Text by Master
# this_file: samples/proof_text_by_master.py
"""Render the same text once per master, stacked, to compare weight and width at a glance.

Each row is drawn from that master's outlines with its line width in units.
Type text (use /glyphname for unencoded glyphs), adjust the size and scroll
through the masters. Advance widths only: kerning is not applied. Nothing in
the font changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Text by Master"
KEY = "proof_text_by_master"
DEFAULT_TEXT = "Hamburgefonstiv"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def font_maps():
    """({code point: glyph name}, {glyph names}) of the current font."""
    font = fontlab.CurrentFont()
    cmap, names = {}, set()
    for glyph in (font.glyphs if font is not None else []):
        names.add(glyph.name)
        for code in glyph.unicodes:
            cmap.setdefault(code, glyph.name)
    return cmap, names


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


class MasterRows(QtGui.QWidget):
    """Custom painter: one labelled row per master."""

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.paint_error = ""
        self.on_error = None  # dialog hook: show drawing errors in the status label
        self.rows, self.px_size, self.upm, self.frame = [], 48, 1000.0, (-250.0, 750.0)

    def set_content(self, rows, size, upm, frame):
        self.rows, self.px_size, self.upm, self.frame = rows, size, float(upm), frame
        scale = size / self.upm
        line = (frame[1] - frame[0]) * scale
        widest = max([sum(a for _, a in run) for _, run, _ in rows] or [0]) * scale
        width, height = int(widest) + 32, int(len(rows) * (line + 34)) + 8
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
        soft.setAlpha(130)
        faint = QtGui.QColor(text)
        faint.setAlpha(30)
        alert = QtGui.QColor("#d33")
        brush = QtGui.QBrush(text)
        scale = self.px_size / self.upm
        descender, ascender = self.frame
        line = (ascender - descender) * scale
        y = 4.0
        for master, run, width_units in self.rows:
            painter.setPen(soft)
            painter.drawText(QtCore.QRectF(16, y, self.width - 32, 18), int(QtCore.Qt.AlignLeft),
                             f"{master}  ·  {width_units:g} units")
            baseline = y + 22 + ascender * scale
            x = 16.0
            for path, advance in run:
                if path is None:
                    painter.setPen(QtGui.QPen(QtGui.QBrush(alert), 1.0))
                    painter.setBrush(QtGui.QBrush())
                    painter.drawRect(QtCore.QRectF(x + 1, baseline - self.px_size * 0.7, advance * scale - 2, self.px_size * 0.7))
                else:
                    painter.save()
                    painter.translate(x, baseline)
                    painter.scale(scale, 0 - scale)
                    painter.fillPath(path, brush)
                    painter.restore()
                x += advance * scale
            y += line + 34
            painter.setPen(QtGui.QPen(QtGui.QBrush(faint), 1.0))
            painter.drawLine(QtCore.QPointF(16, y - 6), QtCore.QPointF(self.width - 16, y - 6))


class TextByMaster(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(600)
        self.resize(720, 600)
        self._connections = []
        self.package = current_package()
        self.cmap, self.names = font_maps()
        self.rows = []

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
        self.size_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setRange(12, 160)
        self.size_slider.setValue(48)
        self.size_label = QtGui.QLabel()
        self.size_label.setMinimumWidth(48)
        form.addWidget(QtGui.QLabel("Text"), 0, 0)
        form.addWidget(self.text, 0, 1, 1, 2)
        form.addWidget(QtGui.QLabel("Size"), 1, 0)
        form.addWidget(self.size_slider, 1, 1)
        form.addWidget(self.size_label, 1, 2)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.view = MasterRows()
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setWidget(self.view)
        self.scroll_area.setWidgetResizable(False)
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

        self._connect(self.text.textChanged, lambda *a: self.refresh())
        self._connect(self.size_slider.valueChanged, lambda *a: self.refresh())
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
        glyph_names = parse_text(self.text.text, self.cmap, self.names)
        self.rows = []
        for master in self.package.masters:
            run = glyph_run(self.package, glyph_names, master)
            self.rows.append((master, run, sum(advance for _, advance in run)))
        frame = (self.package.descender_value, self.package.ascender_value)
        self.view.set_content(self.rows, self.size_slider.value, self.package.upm, frame)
        self.size_label.setText(f"{self.size_slider.value} px")
        missing = sum(1 for n in glyph_names if n is None)
        self.subtitle.setText(f"{len(self.rows)} masters · {len(glyph_names)} glyphs · advance widths, no kerning.")
        widths = [w for _, _, w in self.rows]
        spread = f" · widths {min(widths):g}–{max(widths):g} units" if widths else ""
        self.status.setText(f"{len(self.rows)} rows{spread}" + (f" · {missing} missing" if missing else ""))

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
    dialog = TextByMaster(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
