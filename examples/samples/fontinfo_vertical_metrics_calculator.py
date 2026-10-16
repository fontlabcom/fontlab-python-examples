#FLM: Font Info · Calculate Vertical Metrics
# this_file: samples/fontinfo_vertical_metrics_calculator.py
"""Set hhea, Win (and optionally OS/2 typo) vertical metrics to enclose every glyph, per master.

Bounds are rounded outward and can be padded. FontLab's master ascender, descender and
line gap ARE the OS/2 typo values (measured), so Typo is off by default: turning it on
moves the font's ascender/descender lines to the glyph bounds. Preview before Apply.
"""

import math
import sys
import time

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Calculate Vertical Metrics"
KEY = "fontinfo_vertical_metrics_calculator"


def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def glyph_records(package):
    """Read all Unicode assignments, including secondary encodings, in font order."""
    import FL

    active = current_package()
    if active is None or active.id != package.id:
        raise ValueError("Activate the original font and reopen this tool.")
    legacy = FL.fl.font
    return [
        (legacy[i].name, list(package.findName(legacy[i].name).fgGlyph.unicodes))
        for i in range(len(legacy))
    ]


def write_changes(package, changes):
    """Apply prevalidated (master or None, attribute, old, new) edits; restore on failure."""
    changes = [entry for entry in changes if entry[2] != entry[3]]
    if not changes:
        return {"changed": 0}
    original = package.master
    fontlab.flItems().notifyChangesApplied(TITLE, [package])
    completed = []
    try:
        for master, field, old, new in changes:
            if master is not None:
                package.setMaster(master)
            setattr(package.info, field, new)
            completed.append((master, field, old, new))
    except Exception:
        for master, field, old, new in reversed(completed):
            if master is not None:
                package.setMaster(master)
            setattr(package.info, field, old)
        raise
    finally:
        package.setMaster(original)
        fontlab.flItems().notifyChangesApplied(TITLE, [package])
        fontlab.UpdateAll()
    return {"changed": len(changes)}


METRIC_FIELDS = [
    "openTypeOS2TypoAscender",
    "openTypeOS2TypoDescender",
    "openTypeOS2TypoLineGap",
    "openTypeHheaAscender",
    "openTypeHheaDescender",
    "openTypeHheaLineGap",
    "openTypeOS2WinAscent",
    "openTypeOS2WinDescent",
]


GROUPS = [  # (label, fields): FontLab's ascender/descender/line gap are the typo fields
    ("Typo (= FontLab ascender, descender, line gap)", METRIC_FIELDS[0:3]),
    ("hhea", METRIC_FIELDS[3:6]),
    ("Win", METRIC_FIELDS[6:8]),
]
LABELS = {
    "openTypeOS2TypoAscender": "Typo ascender", "openTypeOS2TypoDescender": "Typo descender",
    "openTypeOS2TypoLineGap": "Typo line gap", "openTypeHheaAscender": "hhea ascender",
    "openTypeHheaDescender": "hhea descender", "openTypeHheaLineGap": "hhea line gap",
    "openTypeOS2WinAscent": "Win ascent", "openTypeOS2WinDescent": "Win descent",
}


def number(value):
    """965.0 -> 965 for display."""
    return int(value) if isinstance(value, float) and value.is_integer() else value


def enclosing_metrics(low, high, padding, gap):
    ascent = max(0, math.ceil(high) + padding)
    descent = min(0, math.floor(low) - padding)
    if ascent > 32767 or descent < -32768:
        raise ValueError("Bounds exceed signed 16-bit typo/hhea limits.")
    return [ascent, descent, gap, ascent, descent, gap, ascent, -descent]


def scan_bounds(package):
    records = glyph_records(package)
    result = {}
    deadline = time.monotonic() + 2.5
    for master in package.masters:
        lows, highs = [], []
        for name, _ in records:
            if time.monotonic() > deadline:
                raise ValueError(
                    "Font too large for an interactive scan; no changes made."
                )
            layer = package.findName(name).findLayer(master)
            if layer is None or layer.isNull:
                continue
            box = layer.boundingBox
            if box.width() == 0 and box.height() == 0:
                continue
            lows.append(box.y())
            highs.append(box.y() + box.height())
        if lows:
            result[master] = (min(lows), max(highs), len(lows))
    return result


def metric_plan(package, bounds, masters, padding, gap, fields=METRIC_FIELDS):
    original = package.master
    changes = []
    try:
        for master in masters:
            if master not in bounds:
                continue
            package.setMaster(master)
            values = enclosing_metrics(*bounds[master][:2], padding, gap)
            changes.extend(
                (master, k, getattr(package.info, k), v)
                for k, v in zip(METRIC_FIELDS, values)
                if k in fields
            )
    finally:
        package.setMaster(original)
    return changes


def run(package, changes):
    return write_changes(package, changes)


class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.package = current_package()
        self._connections = []
        self.setWindowTitle(TITLE)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self.setMinimumWidth(700)
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        face = heading.font
        face.setPointSizeF(face.pointSizeF() * 1.35)
        face.setBold(True)
        heading.setFont(face)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel(
            "Sets hhea and Win (and, if ticked, OS/2 typo) metrics to enclose every glyph, rounded outward. "
            "Typo = FontLab's own ascender/descender lines."
            if self.package
            else "Open a font, then reopen this tool."
        )
        self.subtitle.setWordWrap(True)
        root.addWidget(self.subtitle)
        self.form = QtGui.QGridLayout()
        root.addLayout(self.form)
        self.table = QtGui.QTableWidget()
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(230)
        root.addWidget(self.table, 1)
        self.content = root
        self.status = QtGui.QLabel("")
        self.status.setWordWrap(True)
        muted = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
        muted.setAlpha(170)
        self.status.setStyleSheet("color: " + muted.name(QtGui.QColor.HexArgb))
        self.subtitle.setStyleSheet("color: " + muted.name(QtGui.QColor.HexArgb))
        footer = QtGui.QHBoxLayout()
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setAutoDefault(False)  # keep Apply as the default button
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self.apply_button.setEnabled(self.package is not None)
        self.safe(lambda: (self.setup(), self.refresh()))

    def safe(self, action):
        try:
            return action()
        except Exception as error:  # noqa: BLE001 - contain every PythonQt callback error
            self.status.setText(str(error))
            self.apply_button.setEnabled(False)

    def _connect(self, signal, slot):
        guarded = lambda *args: self.safe(lambda: slot(*args))
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def ensure_font(self):
        active = current_package()
        if active is None or active.id != self.package.id:
            raise ValueError("Activate the original font and reopen this tool.")

    def rows(self, headings, rows):
        self.table.setColumnCount(len(headings))
        self.table.setHorizontalHeaderLabels(headings)
        self.table.setRowCount(len(rows))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                item = QtGui.QTableWidgetItem(str(value))
                if isinstance(value, (float, int)):
                    item.setTextAlignment(
                        int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                    )
                self.table.setItem(row, column, item)

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:  # noqa: BLE001, S110 - already disconnected during native teardown
                pass
        self._connections = []
        windows = getattr(sys, "_fontlab_samples", {})
        if windows.get(KEY) is self:
            windows.pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)

    def setup(self):
        self.bounds = scan_bounds(self.package) if self.package else {}
        self.scope = QtGui.QComboBox()
        self.scope.addItems(
            [
                f"Current master ({self.package.master if self.package else chr(8212)})",
                f"All masters ({len(self.package.masters) if self.package else 0})",
            ]
        )
        self.padding = QtGui.QSpinBox()
        self.padding.setRange(0, 2000)
        self.gap = QtGui.QSpinBox()
        self.gap.setRange(0, 32767)
        for column, (label, control) in enumerate(
            [("Scope", self.scope), ("Padding", self.padding), ("Line gap", self.gap)]
        ):
            self.form.addWidget(QtGui.QLabel(label), 0, column)
            self.form.addWidget(control, 1, column)
        groups = QtGui.QHBoxLayout()
        groups.setSpacing(16)
        self.group_checks = []
        for index, (label, _) in enumerate(GROUPS):
            check = QtGui.QCheckBox(label)
            check.setChecked(index > 0)
            self.group_checks.append(check)
            groups.addWidget(check)
            self._connect(check.toggled, lambda *a: self.refresh())
        groups.addStretch(1)
        self.form.addLayout(groups, 2, 0, 1, 3)
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        for control in (self.padding, self.gap):
            self._connect(control.valueChanged, lambda *a: self.refresh())

    def changes(self):
        masters = (
            list(self.package.masters)
            if self.scope.currentIndex
            else [self.package.master]
        )
        fields = [f for check, (_, group) in zip(self.group_checks, GROUPS) if check.isChecked() for f in group]
        return metric_plan(
            self.package, self.bounds, masters, self.padding.value, self.gap.value, fields
        )

    def refresh(self):
        if self.package is None:
            return
        self.ensure_font()
        self.rows(
            ["Master · field", "Current", "Proposed"],
            [
                (m + " · " + LABELS[k], number(old), number(new))
                for m, k, old, new in self.changes()
            ],
        )
        self.apply_button.setEnabled(
            any(old != new for _, _, old, new in self.changes())
        )
        self.status.setText(
            "Typo/hhea descenders are negative; Win descent is positive. Empty masters skipped. Bounds captured on open; reopen after outline edits."
        )

    def apply(self):
        self.ensure_font()
        self.last_result = run(self.package, self.changes())
        self.refresh()
        self.status.setText(f"Applied {self.last_result['changed']} metric fields")


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
