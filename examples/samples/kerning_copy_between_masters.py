#FLM: Kerning · Copy Between Masters
# this_file: samples/kerning_copy_between_masters.py
"""Copy the kerning of one master to other masters, optionally scaled.

Start a new master's kerning from an existing one, or push corrections from the Regular to its
neighbours. "Replace" makes the targets identical to the source, "Add missing" only adds pairs
the target lacks, "Overwrite matching" updates pairs both have. The summary shows, per target,
how many pairs are added, changed and removed. One Apply is one Undo step for all targets.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Copy Kerning Between Masters"
KEY = "kerning_copy_between_masters"
MODES = [("Replace all pairs", "replace"), ("Add missing pairs only", "missing"), ("Overwrite matching pairs, keep others", "matching")]


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
    exact = value * percent / 100.0
    return int(math.copysign(math.floor(abs(exact) + 0.5), exact))


def plan(source, target, mode, percent):
    """{(left, right): new value or None} turning `target` into the copy of `source`."""
    wanted = {pair: scaled(value, percent) for pair, value in source.items()}
    edits = {}
    for pair, value in wanted.items():
        if mode == "missing" and pair in target:
            continue
        if mode == "matching" and pair not in target:
            continue
        if target.get(pair) != value:
            edits[pair] = value
    if mode == "replace":
        for pair in target:
            if pair not in wanted:
                edits[pair] = None
    return edits


def summary(target, edits):
    added = sum(1 for p, v in edits.items() if v is not None and p not in target)
    removed = sum(1 for v in edits.values() if v is None)
    return added, len(edits) - added - removed, removed


def run(package, source_master, targets, mode, percent):
    """Copy onto every target; one Undo step. Returns {target: (added, changed, removed)}."""
    source = kerning_pairs(package, source_master)
    edits, report = {}, {}
    for master in targets:
        target = kerning_pairs(package, master)
        edits[master] = plan(source, target, mode, percent)
        report[master] = summary(target, edits[master])
    edits = {m: e for m, e in edits.items() if e}
    if edits:
        write_kerning(package, edits)
    return report


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class CopyKerning(QtGui.QDialog):
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
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.filling = False
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
        self.source = QtGui.QComboBox()
        for name in self.masters:
            self.source.addItem(name)
        if self.current_master in self.masters:
            self.source.setCurrentIndex(self.masters.index(self.current_master))
        self.mode = QtGui.QComboBox()
        for label, _ in MODES:
            self.mode.addItem(label)
        self.percent = QtGui.QDoubleSpinBox()
        self.percent.setRange(0.0, 400.0)
        self.percent.setDecimals(1)
        self.percent.setValue(100.0)
        self.percent.setSuffix(" %")
        self.percent.setAlignment(QtCore.Qt.AlignRight)
        form.addWidget(QtGui.QLabel("From"), 0, 0)
        form.addWidget(self.source, 0, 1)
        form.addWidget(QtGui.QLabel("Scale"), 0, 2)
        form.addWidget(self.percent, 0, 3)
        form.addWidget(QtGui.QLabel("Mode"), 1, 0)
        form.addWidget(self.mode, 1, 1, 1, 3)
        form.setColumnStretch(1, 2)
        form.setColumnStretch(3, 1)
        root.addLayout(form)

        targets_label = QtGui.QLabel("To masters")
        targets_label.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(targets_label)
        self.targets = QtGui.QTableWidget(0, 5)
        self.targets.setHorizontalHeaderLabels(["Master", "Pairs now", "Added", "Changed", "Removed"])
        self.targets.verticalHeader().setVisible(False)
        self.targets.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.targets.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.targets.setAlternatingRowColors(True)
        self.targets.setShowGrid(False)
        header = self.targets.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.targets.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.targets.setMinimumHeight(160)
        root.addWidget(self.targets, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Copy")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self.checked = {m: False for m in self.masters}
        self._connect(self.source.currentIndexChanged, lambda *a: self.rebuild())
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.percent.valueChanged, lambda *a: self.refresh())
        self._connect(self.targets.itemChanged, lambda item: self.toggled(item))
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.rebuild()

    def _connect(self, signal, slot):
        def guarded(*args):
            # An exception escaping a PythonQt slot can take FontLab down: report it instead.
            try:
                return slot(*args)
            except Exception as error:
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def source_master(self):
        return self.masters[self.source.currentIndex] if self.masters else ""

    def chosen_targets(self):
        return [m for m in self.masters if self.checked.get(m) and m != self.source_master()]

    def set_targets(self, names):
        """Tick exactly these target masters (used by scripts and tests)."""
        self.checked = {m: m in names for m in self.masters}
        self.refresh()

    def toggled(self, item):
        if self.filling or item.column() != 0:
            return
        self.checked[item.text()] = item.checkState() == QtCore.Qt.Checked
        self.refresh()

    def rebuild(self):
        """One checkable row per target master; rebuilt only when the source changes."""
        others = [m for m in self.masters if m != self.source_master()]
        self.filling = True
        self.targets.setRowCount(len(others))
        for row, master in enumerate(others):
            name = QtGui.QTableWidgetItem(master)
            name.setCheckState(QtCore.Qt.Checked if self.checked.get(master) else QtCore.Qt.Unchecked)
            self.targets.setItem(row, 0, name)
            for column in range(1, 5):
                item = QtGui.QTableWidgetItem("")
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.targets.setItem(row, column, item)
        self.filling = False
        self.refresh()

    def refresh(self):
        """Update the numbers in place: items are never replaced inside their own signal."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        source_name = self.source_master()
        source = kerning_pairs(self.package, source_name)
        self.subtitle.setText(f"{source_name} has {len(source)} pairs. Tick the masters that receive them.")
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        plain = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        self.filling = True
        total = 0
        for row in range(self.targets.rowCount):
            name = self.targets.item(row, 0)
            master = name.text()
            name.setCheckState(QtCore.Qt.Checked if self.checked.get(master) else QtCore.Qt.Unchecked)
            target = kerning_pairs(self.package, master)
            numbers = [len(target), "", "", ""]
            if self.checked.get(master):
                added, changed, removed = summary(target, plan(source, target, self.mode_key(), self.percent.value))
                numbers = [len(target), added, changed, removed]
                total += added + changed + removed
            for column, value in enumerate(numbers, 1):
                item = self.targets.item(row, column)
                item.setText(str(value))
                item.setForeground(QtGui.QBrush(accent if column > 1 and value else plain))
        self.filling = False
        chosen = self.chosen_targets()
        self.status.setText(f"{total} pair edits in {len(chosen)} master{'s' if len(chosen) != 1 else ''}" if chosen
                            else "Tick at least one target master")
        self.apply_button.setEnabled(bool(chosen) and total > 0)

    def mode_key(self):
        return MODES[self.mode.currentIndex][1]

    def apply(self):
        result = run(self.package, self.source_master(), self.chosen_targets(), self.mode_key(), self.percent.value)
        self.last_result = result
        fontlab.UpdateAll()
        self.refresh()
        self.status.setText("Copied: " + " · ".join(f"{m} +{a} ~{c} −{r}" for m, (a, c, r) in result.items()))

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
    dialog = CopyKerning(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
