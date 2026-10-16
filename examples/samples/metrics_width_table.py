#FLM: Metrics · Width Table
# this_file: samples/metrics_width_table.py
"""Advance widths of the selected glyphs across all masters, sortable, with odd progressions flagged.

In a weight family the widths usually grow (or shrink) steadily from master to master. A glyph
whose width goes up and then down again is flagged: often a spacing slip. Click a column header
to sort; "Select flagged" selects those glyphs in the Font window. Nothing is edited.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Width Table"
KEY = "metrics_width_table"


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


def select_in_font(names):
    """Select exactly these glyphs in the Font window (legacy FL selection API)."""
    import FL

    font = FL.fl.font
    wanted = set(names)
    for i in range(len(font)):
        FL.fl.Select(i, 1 if font[i].name in wanted else 0)


# ---------------------------------------------------------------- core
def widths(glyph, masters):
    """[width or None] in master order."""
    out = []
    for master in masters:
        layer = glyph.findLayer(master)
        out.append(None if layer is None or layer.isNull else round(layer.advanceWidth))
    return out


def progression(values):
    """'rising', 'falling', 'flat' or 'mixed' for a list of widths (None ignored)."""
    known = [v for v in values if v is not None]
    steps = [b - a for a, b in zip(known, known[1:])]
    if all(s == 0 for s in steps):
        return "flat"
    if all(s >= 0 for s in steps):
        return "rising"
    if all(s <= 0 for s in steps):
        return "falling"
    return "mixed"


def report(glyphs, masters):
    """[(name, [widths], progression)] for the glyphs, in the given order."""
    rows = []
    for glyph in glyphs:
        values = widths(glyph, masters)
        rows.append((glyph.name, values, progression(values)))
    return rows


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class WidthTable(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(560)
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.rows = []
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

        options = QtGui.QHBoxLayout()
        self.only_flagged = QtGui.QCheckBox("Show only mixed progressions")
        options.addWidget(self.only_flagged)
        options.addStretch(1)
        root.addLayout(options)

        headers = ["Glyph"] + self.masters + ["Progression"]
        self.table = QtGui.QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(240)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select flagged")
        self.select_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.only_flagged.toggled, lambda *a: self.fill())
        self._connect(self.select_button.clicked, lambda *a: self.select_flagged())
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

    def flagged(self):
        return [name for name, _, trend in self.rows if trend == "mixed"]

    def refresh(self):
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
        else:
            self.subtitle.setText(f"{count} glyph{'s' if count != 1 else ''} × {len(self.masters)} masters, "
                                  f"masters in font order: {' → '.join(self.masters)}")
        self.rows = report(self.glyphs, self.masters)
        self.fill()

    def fill(self):
        warn = QtGui.QColor("#d33")
        shown = [r for r in self.rows if not self.only_flagged.isChecked() or r[2] == "mixed"]
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(shown))
        for row, (name, values, trend) in enumerate(shown):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(name))
            for column, value in enumerate(values, 1):
                item = QtGui.QTableWidgetItem("–")
                if value is not None:
                    item.setData(QtCore.Qt.DisplayRole, value)  # an int sorts numerically
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
            flag = QtGui.QTableWidgetItem("⚠ mixed" if trend == "mixed" else trend)
            flag.setTextAlignment(int(QtCore.Qt.AlignCenter))
            if trend == "mixed":
                bold = flag.font()
                bold.setBold(True)
                flag.setFont(bold)
                flag.setForeground(QtGui.QBrush(warn))
            self.table.setItem(row, len(values) + 1, flag)
        self.table.setSortingEnabled(True)
        flagged = self.flagged()
        self.status.setText(f"{len(flagged)} of {len(self.rows)} glyphs with a mixed progression")
        self.select_button.setEnabled(bool(flagged))

    def table_values(self):
        """{glyph: [widths]} as shown (used by tests and handy for copying)."""
        out = {}
        for row in range(self.table.rowCount):
            name = self.table.item(row, 0).text()
            out[name] = [self.table.item(row, c).data(QtCore.Qt.DisplayRole) for c in range(1, len(self.masters) + 1)]
        return out

    def select_flagged(self):
        flagged = self.flagged()
        select_in_font(flagged)
        fontlab.UpdateAll()
        self.status.setText(f"Selected {len(flagged)} glyph{'s' if len(flagged) != 1 else ''} in the Font window")

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
    dialog = WidthTable(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
