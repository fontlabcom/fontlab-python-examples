#FLM: Kerning · Compare Masters
# this_file: samples/kerning_compare_masters.py
"""Line up every kerning pair across all masters and flag the ones that look inconsistent.

Each row is one pair (glyph or @class sides) with its value on every master; a pair missing
on a master shows a dash. Rows are flagged when the sign flips between masters, when a pair
exists on some masters only, or when neighbouring masters differ by more than the jump
threshold. Tick "Only flagged" to proof just those. Nothing is edited.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Compare Kerning Across Masters"
KEY = "kerning_compare_masters"


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
def table(package, masters):
    """{(left, right): [value or None per master]} sorted by pair."""
    per_master = [kerning_pairs(package, m) for m in masters]
    keys = sorted(set().union(*per_master)) if per_master else []
    return {k: [p.get(k) for p in per_master] for k in keys}


def flags(values, threshold):
    """Reasons a row looks inconsistent: 'sign', 'missing', 'jump'."""
    present = [v for v in values if v is not None]
    reasons = []
    if any(v < 0 for v in present) and any(v > 0 for v in present):
        reasons.append("sign")
    if len(present) < len(values):
        reasons.append("missing")
    if any(abs(b - a) > threshold for a, b in zip(present, present[1:])):
        reasons.append("jump")
    return reasons


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class CompareMasters(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(620)
        self.resize(680, 620)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.rows = {}
        self.shown = []
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

        controls = QtGui.QHBoxLayout()
        controls.setSpacing(10)
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("Filter pairs, e.g. A or @L_")
        self.threshold = QtGui.QSpinBox()
        self.threshold.setRange(0, 1000)
        self.threshold.setValue(40)
        self.threshold.setSuffix(" units")
        self.threshold.setAlignment(QtCore.Qt.AlignRight)
        self.only_flagged = QtGui.QCheckBox("Only flagged")
        controls.addWidget(self.search, 1)
        controls.addWidget(QtGui.QLabel("Jump above"))
        controls.addWidget(self.threshold)
        controls.addWidget(self.only_flagged)
        root.addLayout(controls)

        self.table = QtGui.QTableWidget(0, len(self.masters) + 2)
        self.table.setHorizontalHeaderLabels(["Pair"] + self.masters + ["Flags"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(260)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.reload_button = QtGui.QPushButton("Reload")
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self._connect(self.search.textChanged, lambda *a: self.fill())
        self._connect(self.threshold.valueChanged, lambda *a: self.fill())
        self._connect(self.only_flagged.toggled, lambda *a: self.fill())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.reload()

    def _connect(self, signal, slot):
        def guarded(*args):
            # An exception escaping a PythonQt slot can take FontLab down: report it instead.
            try:
                return slot(*args)
            except Exception as error:
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def reload(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        self.rows = table(self.package, self.masters)
        self.subtitle.setText(f"{len(self.rows)} pairs across {len(self.masters)} masters. Flags: sign = the value "
                              "changes sign, missing = absent on some masters, jump = neighbouring masters "
                              "differ by more than the threshold.")
        self.fill()

    def fill(self):
        needle = self.search.text.strip()
        threshold = self.threshold.value
        warn = QtGui.QColor(196, 72, 48)
        self.shown = []
        for (left, right), values in self.rows.items():
            if needle and needle not in left and needle not in right:
                continue
            reasons = flags(values, threshold)
            if self.only_flagged.checked and not reasons:
                continue
            self.shown.append(((left, right), values, reasons))
        self.table.setRowCount(len(self.shown))
        for row, ((left, right), values, reasons) in enumerate(self.shown):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(f"{left}  {right}"))
            for column, value in enumerate(values, 1):
                item = QtGui.QTableWidgetItem("–" if value is None else f"{value:g}")
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
            note = QtGui.QTableWidgetItem(", ".join(reasons))
            if reasons:
                note.setForeground(QtGui.QBrush(warn))
            self.table.setItem(row, len(values) + 1, note)
        flagged = sum(1 for values in self.rows.values() if flags(values, threshold))
        self.status.setText(f"{len(self.shown)} rows shown · {flagged} of {len(self.rows)} pairs flagged")

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
    dialog = CompareMasters(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
