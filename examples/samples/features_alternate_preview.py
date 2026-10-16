#FLM: OpenType · Alternate Glyph Proof
# this_file: samples/features_alternate_preview.py
"""Compare a base glyph and its suffixed alternates in each master. Read-only; outlines share one scale per row.

Standalone PythonQt tool; feature data is shared by all masters.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui


def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def glyph_names():
    font = fontlab.CurrentFont()
    return sorted(g.name for g in font.glyphs) if font is not None else []


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
    color.setAlpha(160)
    return color.name(QtGui.QColor.HexArgb)

TITLE = 'Alternate Glyph Proof'
KEY = "features_alternate_preview"
SUBTITLE = 'Compare a base glyph and its suffixed alternates in each master. Read-only; outlines share one scale per row.'
ACTION = 'Refresh proof'


def layer_path(layer):
    """The layer's outline as one QPainterPath in font units (y up), components placed."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        for part in (shape.closedPath, shape.openedPath):
            if part is not None and not part.isEmpty():
                path.addPath(shape.transform.map(part))
    return path


def run(names, base):
    return ([base] if base in names else []) + sorted(name for name in names if name.startswith(base + "."))


class Proof(QtGui.QWidget):
    def __init__(self, owner):
        QtGui.QWidget.__init__(self, owner)
        self.owner = owner
        self._error = ""

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        try:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            self.draw_proof(painter)
        except Exception as error:
            self._error = str(error)
            self.owner.status.setText("Proof error: " + self._error)
        finally:
            painter.end()

    def draw_proof(self, painter):
        owner = self.owner
        names = getattr(owner, "preview_names", [])
        masters = getattr(owner, "chosen_masters", [])
        text_color = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        painter.setPen(text_color)
        if not names:
            painter.drawText(20, 45, "Enter an existing base glyph name to see its alternates.")
            return
        # Wrap columns into strips instead of shrinking a large family to unreadable thumbnails.
        columns = max(1, int(self.width / 150))
        strips = (len(names) + columns - 1) // columns  # the dialog sizes the canvas in refresh()
        cell_width = self.width / min(columns, len(names))
        for master_index, master in enumerate(masters):
            layers = []
            for name in names:
                glyph = owner.package.findName(name)
                layer = glyph.findLayer(master) if glyph is not None else None
                layers.append(layer if layer is not None and not layer.isNull else None)
            boxes = [layer.boundingBox for layer in layers if layer is not None]
            low = min([box.y() for box in boxes] + [0])
            high = max([box.y() + box.height() for box in boxes] + [1])
            widest = max([box.width() for box in boxes] + [1])
            scale = min((cell_width - 24) / max(1, widest), 130 / max(1, high - low))
            for index, (name, layer) in enumerate(zip(names, layers)):
                x = (index % columns) * cell_width
                y = (master_index * strips + index // columns) * 200
                painter.setPen(text_color)
                painter.drawText(int(x + 10), int(y + 18), master)
                label = QtGui.QFontMetrics(self.font).elidedText(name, QtCore.Qt.ElideRight, int(cell_width - 20))
                painter.drawText(int(x + 10), int(y + 190), label)
                if layer is None:
                    painter.drawText(int(x + 10), int(y + 90), "Missing layer")
                    continue
                path = layer_path(layer)
                box = layer.boundingBox
                transform = QtGui.QTransform(scale, 0, 0, -scale,
                    x + (cell_width - box.width() * scale) / 2 - box.x() * scale,
                    y + 35 + high * scale)
                painter.fillPath(transform.map(path), QtGui.QBrush(text_color))

class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self._connections = []
        self.package = current_package()
        self.font_data = fontlab.CurrentFont() if self.package else None
        self.names = glyph_names() if self.package else []
        self.last_result = None
        self.setWindowTitle(TITLE)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self.setMinimumWidth(640)
        self.resize(780, 620)
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel(SUBTITLE if self.package else "Open a font, then run this script again.")
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet("color: " + muted(self))
        root.addWidget(self.subtitle)
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet("color: " + muted(self))
        form = QtGui.QGridLayout()
        self.base = QtGui.QLineEdit("a")
        glyph = fontlab.CurrentGlyph() if self.package else None
        if glyph is not None:
            self.base.setText(glyph.name.split(".", 1)[0])
        self.scope = QtGui.QComboBox()
        self.masters = list(self.package.masters) if self.package else []
        self.scope.addItem("Current master (" + (self.package.master if self.package else "none") + ")")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Base glyph"), 0, 0)
        form.addWidget(self.base, 0, 1)
        form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        form.addWidget(self.scope, 1, 1)
        root.addLayout(form)
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.canvas = Proof(self)
        self.scroll_area.setWidget(self.canvas)
        root.addWidget(self.scroll_area, 1)
        self._connect(self.base.textChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        footer = QtGui.QHBoxLayout()
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.close_button)
        self.apply_button = QtGui.QPushButton(ACTION)
        self.apply_button.setDefault(True)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._safe(self.refresh)

    def _safe(self, callback):
        try:
            callback()
        except Exception as error:
            self.status.setText(str(error))
            self.apply_button.setEnabled(False)

    def _connect(self, signal, slot):
        # Keep a plain Python receiver and contain every signal exception.
        wrapped = lambda *args: self._safe(lambda: slot(*args))
        signal.connect(wrapped)
        self._connections.append((signal, wrapped))


    def refresh(self):
        self.preview_names = run(self.names, self.base.text.strip()) if self.base.text.strip() else []
        self.chosen_masters = ([self.package.master] if self.scope.currentIndex == 0 else self.masters) if self.package else []
        columns = max(1, int(self.scroll_area.viewport().width / 150))
        strips = max(1, (len(self.preview_names) + columns - 1) // columns)
        self.canvas.setMinimumHeight(max(260, len(self.chosen_masters) * strips * 200))
        self.canvas._error = ""
        self.canvas.update()
        self.apply_button.setEnabled(bool(self.preview_names))
        self.status.setText(f"{len(self.preview_names)} glyphs × {len(self.chosen_masters)} masters · scroll to see every row")

    def apply(self):
        self.refresh()
        self.last_result = {"names": self.preview_names, "masters": self.chosen_masters}

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        windows = sys.__dict__.get("_fontlab_samples", {})
        if windows.get(KEY) is self:
            windows.pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = Dialog(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
