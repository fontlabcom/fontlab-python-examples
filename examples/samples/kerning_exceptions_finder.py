#FLM: Kerning · Exceptions Finder
# this_file: samples/kerning_exceptions_finder.py
"""Find kerning exceptions: pairs that override a class pair, and remove the ones you tick.

An exception is a pair whose glyph side belongs to a kerning class that already has a pair
with the same partner (A V overriding @A V). Exceptions with the same value as the class pair
are redundant and safe to delete; the others are deliberate overrides worth a second look.
Tick rows (or "Tick redundant") and Remove; one Undo step for all masters.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Kerning Exceptions"
KEY = "kerning_exceptions_finder"


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


def class_maps(package, master):
    """({glyph: '@left class'}, {glyph: '@right class'}) of one master."""
    left, right = {}, {}
    for name, (members, mode) in package.kerning(master).groups.items():
        for glyph in members:
            if mode in ("KernLeft", "KernBothSide"):
                left.setdefault(glyph, "@" + name)
            if mode in ("KernRight", "KernBothSide"):
                right.setdefault(glyph, "@" + name)
    return left, right


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
def exceptions(pairs, left_classes, right_classes):
    """[(pair, value, overridden pair, its value)] for pairs that override a broader class pair."""
    found = []
    for (left, right), value in sorted(pairs.items()):
        lc = left_classes.get(left) if not left.startswith("@") else None
        rc = right_classes.get(right) if not right.startswith("@") else None
        broader = [(left, rc), (lc, right), (lc, rc)]
        for candidate in broader:
            if None not in candidate and candidate in pairs:
                found.append(((left, right), value, candidate, pairs[candidate]))
                break
    return found


def find(package, masters):
    """[(master, pair, value, overridden, overridden value)] over the masters."""
    rows = []
    for master in masters:
        left, right = class_maps(package, master)
        for pair, value, broader, broader_value in exceptions(kerning_pairs(package, master), left, right):
            rows.append((master, pair, value, broader, broader_value))
    return rows


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class ExceptionsFinder(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(640)
        self.resize(680, 560)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.rows = []
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

        form = QtGui.QHBoxLayout()
        form.setSpacing(10)
        form.addWidget(QtGui.QLabel("Masters"))
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(self.scope, 1)
        self.tick_redundant = QtGui.QPushButton("Tick redundant")
        self.tick_none = QtGui.QPushButton("Untick all")
        form.addWidget(self.tick_redundant)
        form.addWidget(self.tick_none)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Exception", "Master", "Value", "Overrides", "Class value", "Δ"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
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
        self.apply_button = QtGui.QPushButton("Remove ticked")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.table.itemChanged, lambda *a: self.count())
        self._connect(self.tick_redundant.clicked, lambda *a: self.tick(lambda row: row[2] == row[4]))
        self._connect(self.tick_none.clicked, lambda *a: self.tick(lambda row: False))
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
        """Re-scan the kerning (call again after editing kerning elsewhere)."""
        self.rows = find(self.package, self.chosen_masters()) if self.package else []
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            redundant = sum(1 for r in self.rows if r[2] == r[4])
            self.subtitle.setText(f"{len(self.rows)} exceptions, {redundant} of them redundant (same value as the class pair "
                                  "they override). Tick the ones to delete.")
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        dim = QtGui.QColor(muted(self))
        self.filling = True
        self.table.setRowCount(len(self.rows))
        for row, (master, pair, value, broader, broader_value) in enumerate(self.rows):
            name = QtGui.QTableWidgetItem(f"{pair[0]}  {pair[1]}")
            name.setCheckState(QtCore.Qt.Unchecked)
            self.table.setItem(row, 0, name)
            self.table.setItem(row, 1, QtGui.QTableWidgetItem(master))
            delta = value - broader_value
            cells = [(2, f"{value:g}"), (3, f"{broader[0]}  {broader[1]}"), (4, f"{broader_value:g}"),
                     (5, "same" if not delta else f"{delta:+g}")]
            for column, text in cells:
                item = QtGui.QTableWidgetItem(text)
                if column != 3:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if column == 5:
                    item.setForeground(QtGui.QBrush(dim if not delta else accent))
                self.table.setItem(row, column, item)
        self.filling = False
        self.count()

    def ticked(self):
        return [self.rows[r] for r in range(self.table.rowCount)
                if self.table.item(r, 0).checkState() == QtCore.Qt.Checked]

    def tick(self, rule):
        self.filling = True
        for r, row in enumerate(self.rows):
            self.table.item(r, 0).setCheckState(QtCore.Qt.Checked if rule(row) else QtCore.Qt.Unchecked)
        self.filling = False
        self.count()

    def count(self):
        if self.filling:
            return
        ticked = self.ticked()
        self.status.setText(f"{len(ticked)} of {len(self.rows)} ticked" if self.rows else "No exceptions found")
        self.apply_button.setEnabled(bool(ticked))
        self.tick_redundant.setEnabled(any(r[2] == r[4] for r in self.rows))

    def apply(self):
        edits = {}
        for master, pair, _, _, _ in self.ticked():
            edits.setdefault(master, {})[pair] = None
        if edits:
            write_kerning(self.package, edits)
        self.last_result = {m: len(p) for m, p in edits.items()}
        fontlab.UpdateAll()
        self.refresh()
        self.status.setText(f"Removed {sum(self.last_result.values())} exceptions")

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
    dialog = ExceptionsFinder(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
