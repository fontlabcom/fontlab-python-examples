#FLM: Kerning · Remove Small Pairs
# this_file: samples/kerning_remove_small.py
"""Delete kerning pairs whose value is smaller than a threshold, on one or all masters.

Tiny pairs (±1 … ±5 units) are invisible in print, bloat the kern feature and often come from
auto-kerning or interpolation. The preview lists every pair that would go, with the count per
master; zero pairs are included. Class pairs (@name) count like glyph pairs. One Apply is one
Undo step for all masters.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Remove Small Kerning"
KEY = "kerning_remove_small"


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


def native_side(name):
    return (name[1:], True) if name.startswith("@") else (name, False)


def write_kerning(package, edits):
    """Apply {master: {(left, right): value or None}} as one Undo step (None deletes the pair)."""
    items = [package, package.mastersContainer(), package.kerningContainer()]
    package.checkInitHistoryState(0)
    fontlab.flItems.notifyChangesApplied(TITLE, items)
    for master, pairs in edits.items():
        kerning = package.kerning(master)
        for (left, right), value in pairs.items():
            key = (native_side(left), native_side(right))
            if value is None:
                kerning.remove(key)
            else:
                kerning.set(key, int(value))
    fontlab.flItems.notifyChangesApplied(TITLE, items)


# ---------------------------------------------------------------- core
def small_pairs(package, masters, threshold):
    """{master: [(left, right, value)]} with |value| < threshold, sorted by size then name."""
    found = {}
    for master in masters:
        rows = [(l, r, v) for (l, r), v in kerning_pairs(package, master).items() if abs(v) < threshold]
        found[master] = sorted(rows, key=lambda row: (abs(row[2]), row[0], row[1]))
    return found


def run(package, masters, threshold):
    """Remove the small pairs; one Undo step. Returns {master: removed count}."""
    found = small_pairs(package, masters, threshold)
    edits = {m: {(l, r): None for l, r, _ in rows} for m, rows in found.items() if rows}
    if edits:
        write_kerning(package, edits)
    return {m: len(rows) for m, rows in found.items()}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def make_table(headers):
    table = QtGui.QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
    table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
    header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
    table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    table.setMinimumHeight(220)
    return table


class RemoveSmall(QtGui.QDialog):
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
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.found = {}
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
        self.threshold = QtGui.QSpinBox()
        self.threshold.setRange(1, 500)
        self.threshold.setValue(5)
        self.threshold.setPrefix("|value| < ")
        self.threshold.setSuffix(" units")
        self.threshold.setAlignment(QtCore.Qt.AlignRight)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Remove"), 0, 0)
        form.addWidget(self.threshold, 0, 1)
        form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        form.addWidget(self.scope, 1, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = make_table(["Pair", "Master", "Value"])
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Remove")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.threshold.valueChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
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

    def chosen_masters(self):
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.found = {}
        else:
            self.found = small_pairs(self.package, self.chosen_masters(), self.threshold.value)
            total = sum(len(kerning_pairs(self.package, m)) for m in self.chosen_masters())
            self.subtitle.setText(f"{total} pairs in {len(self.chosen_masters())} master{'s' if len(self.chosen_masters()) != 1 else ''}; "
                                  f"pairs closer to zero than the threshold are deleted.")
        rows = [(f"{l}  {r}", m, v) for m, found in self.found.items() for l, r, v in found]
        warn = QtGui.QColor("#d33")
        self.table.setRowCount(len(rows))
        for row, (pair, master, value) in enumerate(rows):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(pair))
            self.table.setItem(row, 1, QtGui.QTableWidgetItem(master))
            item = QtGui.QTableWidgetItem(f"{value:g}")
            item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
            item.setForeground(QtGui.QBrush(warn))
            self.table.setItem(row, 2, item)
        counts = " · ".join(f"{m} {len(f)}" for m, f in self.found.items())
        self.status.setText(f"{len(rows)} to remove ({counts})" if rows else "No pairs below the threshold")
        self.apply_button.setEnabled(bool(rows))

    def apply(self):
        result = run(self.package, self.chosen_masters(), self.threshold.value)
        self.last_result = result
        fontlab.UpdateAll()
        self.refresh()
        self.status.setText(f"Removed {sum(result.values())} pairs (" + " · ".join(f"{m} {n}" for m, n in result.items()) + ")")

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
    dialog = RemoveSmall(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
