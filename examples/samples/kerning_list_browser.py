#FLM: Kerning · Pair List
# this_file: samples/kerning_list_browser.py
"""Browse every kerning pair of a master: filter, sort by any column, export to CSV.

Type in the filter to keep pairs whose left or right side contains the text (glyph or @class
name); "=" anchors a whole side, so "=T" shows pairs with exactly T on one side. Click a header
to sort; values sort numerically. Export writes the pairs shown to a CSV file. Read-only.
"""

import csv
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Kerning Pairs"
KEY = "kerning_list_browser"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def kerning_pairs(package, master):
    """{(left, right): value} of one master; class sides are written '@name'."""
    pairs = {}
    for pair, value in package.kerning(master).items():
        left = ("@" if pair.left.mode == "groupMode" else "") + pair.left.id
        right = ("@" if pair.right.mode == "groupMode" else "") + pair.right.id
        pairs[(left, right)] = value
    return pairs


# ---------------------------------------------------------------- core
def matches(pair, text):
    """Filter rule: substring of either side; '=name' must equal a whole side."""
    text = text.strip()
    if not text:
        return True
    if text.startswith("="):
        return text[1:] in pair
    return any(text in side for side in pair)


def filtered(pairs, text):
    return sorted((l, r, v) for (l, r), v in pairs.items() if matches((l, r), text))


def export_csv(rows, master, path):
    """Write left,right,value,master rows; returns the number of pairs written."""
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["left", "right", "value", "master"])
        for left, right, value in rows:
            writer.writerow([left, right, f"{value:g}", master])
    return len(rows)


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class PairList(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(520)
        self.resize(560, 640)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.pairs = {}
        self.rows = []
        self.file_dialog = None
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
        self.master = QtGui.QComboBox()
        for name in self.masters:
            self.master.addItem(name)
        if self.current_master in self.masters:
            self.master.setCurrentIndex(self.masters.index(self.current_master))
        self.filter = QtGui.QLineEdit()
        self.filter.setPlaceholderText("Filter: T, @L_A, =V …")
        self.filter.setClearButtonEnabled(True)
        form.addWidget(QtGui.QLabel("Master"), 0, 0)
        form.addWidget(self.master, 0, 1)
        form.addWidget(QtGui.QLabel("Filter"), 1, 0)
        form.addWidget(self.filter, 1, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Left", "Right", "Value"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(260)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.export_button = QtGui.QPushButton("Export CSV…")
        self.export_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.export_button)
        root.addLayout(footer)

        self._connect(self.master.currentIndexChanged, lambda *a: self.load())
        self._connect(self.filter.textChanged, lambda *a: self.fill())
        self._connect(self.export_button.clicked, lambda *a: self.ask_path())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.load()

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

    def load(self):
        self.pairs = kerning_pairs(self.package, self.chosen_master()) if self.package else {}
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            classes = sum(1 for l, r in self.pairs if l.startswith("@") or r.startswith("@"))
            self.subtitle.setText(f"{self.chosen_master()}: {len(self.pairs)} pairs, {classes} of them with a class side")
        self.fill()

    def fill(self):
        self.rows = filtered(self.pairs, self.filter.text)
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.rows))
        for row, (left, right, value) in enumerate(self.rows):
            for column, text in enumerate((left, right)):
                item = QtGui.QTableWidgetItem(text)
                if text.startswith("@"):
                    item.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, column, item)
            item = QtGui.QTableWidgetItem()
            item.setData(QtCore.Qt.DisplayRole, int(value) if value == int(value) else value)
            item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
            self.table.setItem(row, 2, item)
        self.table.setSortingEnabled(True)
        shown = f"{len(self.rows)} of {len(self.pairs)} pairs" if self.filter.text.strip() else f"{len(self.rows)} pairs"
        self.status.setText(shown)
        self.export_button.setEnabled(bool(self.rows))

    def shown_rows(self):
        """Rows in the table's current (possibly sorted) order."""
        out = []
        for row in range(self.table.rowCount):
            out.append((self.table.item(row, 0).text(), self.table.item(row, 1).text(),
                        float(self.table.item(row, 2).data(QtCore.Qt.DisplayRole))))
        return out

    def ask_path(self):
        """Non-modal save dialog (open(), never a blocking modal loop): FontLab keeps running."""
        if self.file_dialog is None:
            dialog = QtGui.QFileDialog(self, "Export kerning pairs")
            dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            dialog.setNameFilter("CSV files (*.csv)")
            dialog.setDefaultSuffix("csv")
            dialog.setOption(QtGui.QFileDialog.DontUseNativeDialog, True)
            self._connect(dialog.fileSelected, lambda path: self.export(path))
            self.file_dialog = dialog
        self.file_dialog.selectFile(f"kerning-{self.chosen_master()}.csv")
        self.file_dialog.open()

    def export(self, path):
        count = export_csv(self.shown_rows(), self.chosen_master(), path)
        self.last_export = {"path": path, "pairs": count}
        self.status.setText(f"Exported {count} pairs to {path}")
        return count

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        if self.file_dialog is not None:
            self.file_dialog.close()
        getattr(sys, "_fontlab_samples", {}).pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = PairList(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
