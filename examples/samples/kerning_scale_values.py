#FLM: Kerning · Scale Values
# this_file: samples/kerning_scale_values.py
"""Scale all kerning values by a percentage on one or all masters.

Loosen a Light master's kerning or tighten a display master's in one go: every pair (glyph and
class pairs alike) is multiplied and rounded to whole units, halves away from zero. Pairs that
become 0 can be deleted. The preview lists every change; one Apply is one Undo step.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Scale Kerning"
KEY = "kerning_scale_values"


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
def scaled(value, percent):
    """value × percent / 100 in whole units, halves away from zero."""
    exact = value * percent / 100.0
    return int(math.copysign(math.floor(abs(exact) + 0.5), exact))


def plan(package, masters, percent, drop_zero):
    """{master: {(left, right): (value, new or None)}} for pairs whose value changes."""
    todo = {}
    for master in masters:
        items = {}
        for pair, value in kerning_pairs(package, master).items():
            new = scaled(value, percent)
            if new == 0 and drop_zero and value != 0:
                items[pair] = (value, None)
            elif new != value:
                items[pair] = (value, new)
        todo[master] = items
    return todo


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


class ScaleKerning(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(540)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.todo = {}
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
        self.percent = QtGui.QDoubleSpinBox()
        self.percent.setRange(0.0, 400.0)
        self.percent.setDecimals(1)
        self.percent.setValue(100.0)
        self.percent.setSuffix(" %")
        self.percent.setAlignment(QtCore.Qt.AlignRight)
        self.drop_zero = QtGui.QCheckBox("Delete pairs that become 0")
        self.drop_zero.setChecked(True)
        form.addWidget(QtGui.QLabel("Scale by"), 0, 0)
        form.addWidget(self.percent, 0, 1)
        form.addWidget(self.drop_zero, 1, 1, 1, 2)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1, 1, 2)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = make_table(["Pair", "Master", "Value", "New value"])
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        for widget in self.inputs():
            signal = widget.toggled if isinstance(widget, QtGui.QCheckBox) else (
                widget.currentIndexChanged if isinstance(widget, QtGui.QComboBox) else widget.valueChanged)
            self._connect(signal, lambda *a: self.refresh())
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
            self.todo = {}
        else:
            self.todo = self.plan()
            total = sum(len(kerning_pairs(self.package, m)) for m in self.chosen_masters())
            self.subtitle.setText(f"{total} pairs in {len(self.chosen_masters())} master{'s' if len(self.chosen_masters()) != 1 else ''}. "
                                  + self.explain())
        rows = [(f"{l}  {r}", m, old, new) for m, items in self.todo.items() for (l, r), (old, new) in sorted(items.items())]
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        warn = QtGui.QColor("#d33")
        self.table.setRowCount(len(rows))
        for row, (pair, master, old, new) in enumerate(rows):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(pair))
            self.table.setItem(row, 1, QtGui.QTableWidgetItem(master))
            for column, value in ((2, f"{old:g}"), (3, "removed" if new is None else f"{new:g}")):
                item = QtGui.QTableWidgetItem(value)
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if column == 3:
                    bold = item.font()
                    bold.setBold(True)
                    item.setFont(bold)
                    item.setForeground(QtGui.QBrush(warn if new is None else accent))
                self.table.setItem(row, column, item)
        counts = " · ".join(f"{m} {len(v)}" for m, v in self.todo.items())
        self.status.setText(f"{len(rows)} pairs change ({counts})" if rows else "Nothing to change")
        self.apply_button.setEnabled(bool(rows))

    def apply(self):
        todo = self.plan()
        edits = {m: {pair: new for pair, (_, new) in items.items()} for m, items in todo.items() if items}
        if edits:
            write_kerning(self.package, edits)
        self.last_result = {m: len(items) for m, items in todo.items()}
        fontlab.UpdateAll()
        self.refresh()
        self.status.setText(f"Changed {sum(self.last_result.values())} pairs (" +
                            " · ".join(f"{m} {n}" for m, n in self.last_result.items()) + ")")

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        getattr(sys, "_fontlab_samples", {}).pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)

    def inputs(self):
        return [self.percent, self.drop_zero, self.scope]

    def plan(self):
        return plan(self.package, self.chosen_masters(), self.percent.value, self.drop_zero.isChecked())

    def explain(self):
        return f"Every value is multiplied by {self.percent.value:g} % and rounded to whole units."


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = ScaleKerning(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
