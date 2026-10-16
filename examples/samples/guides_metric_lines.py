#FLM: Guides · Metric Reference Lines
# this_file: samples/guides_metric_lines.py
"""Add named horizontal glyph guides at the font's vertical metrics, plus an offset.

Pick baseline, x-height, cap height, ascender and descender; each master uses its
own metric values. Guides that already exist (same name and position) are not
added twice. Auto layers are skipped. One Apply is one Undo step.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Metric Reference Lines"
KEY = "guides_metric_lines"
METRICS = [("Baseline", None), ("x-height", "xHeight"), ("Cap height", "capsHeight"),
           ("Ascender", "ascender"), ("Descender", "descender")]


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


def master_layers(glyph, masters):
    """[(master, flLayer)] for the masters present in this glyph."""
    found = []
    for master in masters:
        layer = glyph.findLayer(master)
        if layer is not None and not layer.isNull:
            found.append((master, layer))
    return found


def metric_values(package, master):
    """{label: y} of one master's vertical metrics (FontMetrics does not switch masters)."""
    metrics = fontlab.FontMetrics(package, master)
    return {label: float(getattr(metrics, attr)) if attr else 0.0 for label, attr in METRICS}


# ---------------------------------------------------------------- guides
# flGuideLine(QLineF, flags, style): the (angle, point) overload ignores the angle in PythonQt and
# makes free "vector" guides; FontLab's own glyph guides carry these flags (flsnapline.h).
HORIZONTAL, VERTICAL, VECTOR = 0x2000, 0x4000, 0x1000  # flSnaps::Horizontal / Vertical / Vector
GLYPH_GUIDE = 0x102  # SnapObjectsStyle gsGlyphGuideline


def guide_record(guide):
    """(x, y, angle in degrees, name) of an flGuideLine; x is 0 for horizontal, y for vertical guides."""
    point = guide.centerPoint
    angle = round(math.degrees(guide.angle), 2) % 180  # flGuideLine.angle is in radians
    x, y = round(point.x(), 2), round(point.y(), 2)
    return (0.0 if angle == 0 else x, 0.0 if angle == 90 else y, angle, str(guide.name or ""))


def glyph_guides(layer):
    return [g for g in layer.guidelines if not g.isHint]


def new_guide(values):
    """A glyph guide through (x, y) at `angle` degrees (0 horizontal, 90 vertical)."""
    x, y, angle, name = values
    if angle == 0:
        line, flags = QtCore.QLineF(x, y, x + 100, y), HORIZONTAL
    elif angle == 90:
        line, flags = QtCore.QLineF(x, y, x, y + 100), VERTICAL
    else:
        radians = math.radians(angle)
        line, flags = QtCore.QLineF(x, y, x + 100 * math.cos(radians), y + 100 * math.sin(radians)), VECTOR
    guide = fontlab.flGuideLine(line, flags, GLYPH_GUIDE)
    guide.name = name
    return guide


def add_guides(jobs):
    """jobs: [(glyph, layer, [records to add])]. Notify before and after: one Undo step."""
    layers = [layer for _, layer, values in jobs if values]
    glyphs = []
    for glyph, _, values in jobs:
        if values and glyph not in glyphs:
            glyphs.append(glyph)
    if not layers:
        return {"layers": 0, "guides": 0}
    items = layers + glyphs
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    count = 0
    for _, layer, values in jobs:
        if values:
            layer.appendGuidelines([new_guide(v) for v in values])
            count += len(values)
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    fontlab.UpdateAll()
    return {"layers": len(layers), "guides": count}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class MetricLines(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(540)
        palette = self.palette
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % palette.color(QtGui.QPalette.WindowText).name())
        self._connections = []
        self.last_result = None
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""

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
        checks = QtGui.QHBoxLayout()
        checks.setSpacing(14)
        self.metric_checks = {}
        for label, _ in METRICS:
            check = QtGui.QCheckBox(label)
            check.setChecked(True)
            self.metric_checks[label] = check
            checks.addWidget(check)
        checks.addStretch(1)
        self.offset = QtGui.QSpinBox()
        self.offset.setRange(-2000, 2000)
        self.offset.setSuffix(" units")
        self.offset.setAlignment(QtCore.Qt.AlignRight)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Lines"), 0, 0)
        form.addLayout(checks, 0, 1)
        form.addWidget(QtGui.QLabel("Offset"), 1, 0)
        form.addWidget(self.offset, 1, 1)
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Glyph · master", "Guide", "y", "Action"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(220)
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

        for check in self.metric_checks.values():
            self._connect(check.toggled, lambda *a: self.refresh())
        self._connect(self.offset.valueChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal, slot):
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:  # an exception escaping a PythonQt slot can take FontLab down
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    # state
    def chosen_masters(self):
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def plan(self):
        """[(glyph, master, layer, [(record, action)])]; action is add / exists / auto."""
        wanted = [label for label, _ in METRICS if self.metric_checks[label].isChecked()]
        values = {m: metric_values(self.package, m) for m in self.chosen_masters()}
        rows = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()):
                records = [(0.0, round(values[master][label] + self.offset.value, 2), 0.0, label) for label in wanted]
                if layer.autoLayer:
                    rows.append((glyph, master, layer, [(r, "auto layer, skipped") for r in records]))
                    continue
                existing = {guide_record(g) for g in glyph_guides(layer)}
                rows.append((glyph, master, layer, [(r, "exists" if r in existing else "add") for r in records]))
        return rows

    def refresh(self):
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (" …" if count > 8 else "")
            self.subtitle.setText(f"Adds horizontal glyph guides to {count} glyph{'s' if count != 1 else ''}: {names}")
        self.planned = self.plan() if self.glyphs else []
        rows = [(f"{g.name} · {m}", r[3], f"{r[1]:g}", action)
                for g, m, layer, entries in self.planned for r, action in entries]
        ink = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(QtGui.QBrush(accent if column == 3 and text == "add" else ink))
                if column == 2:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
        adds = sum(1 for cells in rows if cells[3] == "add")
        self.apply_button.setEnabled(adds > 0)
        self.status.setText(f"{adds} guide{'s' if adds != 1 else ''} to add")

    def apply(self):
        jobs = [(g, layer, [r for r, action in entries if action == "add"])
                for g, m, layer, entries in self.plan() if not layer.autoLayer]
        self.last_result = add_guides(jobs)
        self.refresh()
        self.status.setText(f"Added {self.last_result['guides']} guides to {self.last_result['layers']} layers")

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
    dialog = MetricLines(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
