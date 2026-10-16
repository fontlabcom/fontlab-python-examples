#FLM: Reports · Empty Glyphs
# this_file: samples/report_empty_glyphs.py
"""List glyphs that have no outlines and no components on some or all masters, and select them.

A glyph empty on one master but drawn on others is usually a mistake;
spaces are empty on purpose and can be hidden. Each master is a column.
Select puts the listed glyphs (or the rows you pick) into the Font window
selection. Nothing in the font changes.
"""

import sys
import unicodedata

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Empty Glyphs"
KEY = "report_empty_glyphs"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def select_in_font_window(names):
    import FL

    font = FL.fl.font
    wanted = set(names)
    FL.fl.Unselect()
    for i in range(len(font)):
        if font[i].name in wanted:
            FL.fl.Select(i)
    fontlab.UpdateAll()
    return [font[i].name for i in range(len(font)) if FL.fl.Selected(i)]


# ---------------------------------------------------------------- core
def is_empty(layer):
    """Nothing drawn: no contours, counting the contours of its components."""
    return not layer.getContours()


def is_whitespace(name, codes):
    if any(unicodedata.category(chr(c)) in ("Zs", "Zl", "Zp", "Cc", "Cf") for c in codes):
        return True
    return name in (".notdef", ".null", "nbspace", "space", "CR", "nonmarkingreturn") or name.endswith("space")


def scan(package, skip_whitespace):
    """[(glyph name, [master, ...] where empty)] in font order."""
    font = fontlab.CurrentFont()
    masters = list(package.masters)
    out = []
    for fg in font.glyphs:
        if skip_whitespace and is_whitespace(fg.name, list(fg.unicodes)):
            continue
        glyph = package.findName(fg.name)
        if glyph is None:
            continue
        empty = []
        for master in masters:
            layer = glyph.findLayer(master)
            if layer is None or is_empty(layer):
                empty.append(master)
        if empty:
            out.append((fg.name, empty))
    return out


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class EmptyGlyphs(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(520)
        self.resize(560, 460)
        self._connections = []
        self.rows = []

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
        self.skip_whitespace = QtGui.QCheckBox("Hide space-like glyphs (empty on purpose)")
        self.skip_whitespace.setChecked(True)
        root.addWidget(self.skip_whitespace)

        self.table = QtGui.QTableWidget(0, 1)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.rescan_button = QtGui.QPushButton("Rescan")
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select in Font window")
        self.select_button.setDefault(True)
        footer.addWidget(self.rescan_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.skip_whitespace.toggled, lambda *a: self.rescan())
        self._connect(self.rescan_button.clicked, lambda *a: self.rescan())
        self._connect(self.select_button.clicked, lambda *a: self.select_rows())
        self._connect(self.table.cellDoubleClicked, lambda row, *a: self.select_rows([row]))
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.rescan()

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

    def rescan(self):
        package = current_package()
        if package is None:
            self.subtitle.setText("Open a font first.")
            self.select_button.setEnabled(False)
            return
        masters = list(package.masters)
        self.rows = scan(package, self.skip_whitespace.isChecked())
        partial = sum(1 for _, empty in self.rows if len(empty) < len(masters))
        self.subtitle.setText(f"{len(self.rows)} glyph{'s' if len(self.rows) != 1 else ''} without outlines on at "
                              f"least one of {len(masters)} masters; {partial} only on some (likely mistakes).")
        self.table.clear()
        self.table.setColumnCount(1 + len(masters))
        self.table.setHorizontalHeaderLabels(["Glyph"] + masters)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        alert = QtGui.QColor("#d33")
        soft = QtGui.QColor(muted(self))
        self.table.setRowCount(len(self.rows))
        for row, (name, empty) in enumerate(self.rows):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(name))
            for column, master in enumerate(masters, start=1):
                item = QtGui.QTableWidgetItem("empty" if master in empty else "✓")
                item.setTextAlignment(int(QtCore.Qt.AlignCenter))
                item.setForeground(QtGui.QBrush(alert if master in empty else soft))
                self.table.setItem(row, column, item)
        self.select_button.setEnabled(bool(self.rows))
        self.status.setText("Double-click a row to select it.")

    def select_rows(self, rows=None):
        if rows is None:
            rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()})
            rows = rows or list(range(len(self.rows)))
        names = [self.rows[r][0] for r in rows if 0 <= r < len(self.rows)]
        selected = select_in_font_window(names)
        self.last_result = {"selected": selected}
        self.status.setText(f"Selected {len(selected)} glyph{'s' if len(selected) != 1 else ''}")

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
    dialog = EmptyGlyphs(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
