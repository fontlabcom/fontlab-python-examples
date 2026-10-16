#FLM: Reports · Font Overview
# this_file: samples/report_font_overview.py
"""A one-screen dashboard of the current font: glyphs, encoding, masters, kerning, composites.

Cards show glyph and code point counts, composites, glyphs without
outlines on the current master, marks and notes; the table lists each
master's vertical metrics and kerning pair count. Click Refresh after
editing. Nothing in the font changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Font Overview"
KEY = "report_font_overview"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def component_names(layer):
    """Base glyph names of the layer's components."""
    names = []
    for shape in layer.shapes:
        base = shape.shapeData.componentGlyph if shape.shapeData is not None else ""
        if base:
            names.append(base)
    return names


# ---------------------------------------------------------------- core
def overview(package):
    """{card: value} and [(master, ascender, caps, x-height, descender, kerning pairs)]."""
    font = fontlab.CurrentFont()
    glyphs = list(font.glyphs)
    masters = list(package.masters)
    current = package.master
    codes = [code for glyph in glyphs for code in glyph.unicodes]
    composites = empty = marked = notes = 0
    for fg in glyphs:
        glyph = package.findName(fg.name)
        if glyph is None:
            continue
        layers = [glyph.findLayer(m) for m in masters]
        layers = [layer for layer in layers if layer is not None]
        if any(component_names(layer) for layer in layers):
            composites += 1
        layer = glyph.findLayer(current)
        if layer is not None and not layer.getContours() and not component_names(layer):
            empty += 1
        marked += 1 if int(glyph.mark or 0) else 0
        notes += 1 if (glyph.note or "").strip() else 0
    cards = {
        "Glyphs": len(glyphs),
        "Encoded glyphs": sum(1 for g in glyphs if list(g.unicodes)),
        "Code points": len(set(codes)),
        "Masters": len(masters),
        "Composites": composites,
        f"Empty on {current}": empty,
        "Marked": marked,
        "With notes": notes,
    }
    rows = []
    for master in masters:
        metrics = fontlab.FontMetrics(package, master)
        rows.append((master, metrics.ascender, metrics.capsHeight, metrics.xHeight, metrics.descender,
                     len(package.kerning(master))))
    return cards, rows


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Overview(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(600)
        self._connections = []
        self.cards, self.rows = {}, []

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

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)
        root.addLayout(self.grid)
        self.card_values = {}

        self.table = QtGui.QTableWidget(0, 6)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setHorizontalHeaderLabels(["Master", "Ascender", "Caps", "x-height", "Descender", "Kern pairs"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(140)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.refresh_button = QtGui.QPushButton("Refresh")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.refresh_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self._connect(self.refresh_button.clicked, lambda *a: self.refresh())
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

    def card(self, index, label):
        frame = QtGui.QFrame()
        frame.setObjectName("card")
        base = self.palette.color(QtGui.QPalette.Base).name()
        border = self.palette.color(QtGui.QPalette.Mid).name()
        frame.setStyleSheet(f"QFrame#card {{ background: {base}; border: 1px solid {border}; border-radius: 8px; }}")
        box = QtGui.QVBoxLayout(frame)
        box.setContentsMargins(12, 10, 12, 10)
        box.setSpacing(2)
        value = QtGui.QLabel("–")
        big = value.font
        big.setPointSizeF(big.pointSizeF() * 1.7)
        big.setBold(True)
        value.setFont(big)
        value.setStyleSheet(f"color: {self.palette.color(QtGui.QPalette.Link).name()}; border: none;")
        caption = QtGui.QLabel(label)
        caption.setStyleSheet(f"color: {muted(self)}; border: none;")
        box.addWidget(value)
        box.addWidget(caption)
        self.grid.addWidget(frame, index // 4, index % 4)
        self.card_values[label] = value

    def refresh(self):
        package = current_package()
        if package is None:
            self.subtitle.setText("Open a font first.")
            return
        self.cards, self.rows = overview(package)
        if set(self.cards) != set(self.card_values):
            while self.grid.count():
                item = self.grid.takeAt(0)
                if item.widget() is not None:
                    item.widget().deleteLater()
            self.card_values = {}
            for index, label in enumerate(self.cards):
                self.card(index, label)
        for label, value in self.cards.items():
            self.card_values[label].setText(f"{value:,}")
        family = package.info.familyName
        self.subtitle.setText(f"{family} · {int(package.upm)} units per em · current master {package.master}")
        self.table.setRowCount(len(self.rows))
        for row, values in enumerate(self.rows):
            for column, value in enumerate(values):
                text = value if column == 0 else f"{value:g}"
                item = QtGui.QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
        self.status.setText("Composites: a component on any master. Empty: no contours and no components.")

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
    dialog = Overview(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
