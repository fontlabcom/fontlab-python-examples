#FLM: Guides · Copy Guides Between Masters
# this_file: samples/guides_copy_between_masters.py
"""Copy the glyph guides of one master to the other masters of the selected glyphs.

Vertical positions can follow each master's advance width (x scaled by the width
ratio), so a guide at the middle of the glyph stays in the middle. Add keeps the
target guides; Replace makes the target equal the source. Guides already there are
not added twice. Auto layers are skipped. One Apply is one Undo step.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Copy Guides Between Masters"
KEY = "guides_copy_between_masters"


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


def write_guides(layer, records):
    """Make the layer's glyph guides equal `records`; unchanged guides are kept (copied with their style)."""
    pool = [(guide_record(g), fontlab.flGuideLine(g)) for g in glyph_guides(layer)]
    planned = []
    for record in records:
        index = next((i for i, (old, _) in enumerate(pool) if old == record), None)
        planned.append((record, pool.pop(index)[1] if index is not None else new_guide(record)))
    layer.removeGuides(True, True)
    left = [guide_record(g) for g in glyph_guides(layer)]  # guides removeGuides leaves in place
    add = []
    for record, guide in planned:
        if record in left:
            left.remove(record)
        else:
            add.append(guide)
    if add:
        layer.appendGuidelines(add)


def replace_guides(jobs):
    """jobs: [(glyph, layer, [records])]. Notify before and after: one Undo step."""
    layers = [layer for _, layer, _ in jobs]
    glyphs = []
    for glyph, _, _ in jobs:
        if glyph not in glyphs:
            glyphs.append(glyph)
    if not layers:
        return {"layers": 0}
    items = layers + glyphs
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    for _, layer, records in jobs:
        write_guides(layer, records)
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    fontlab.UpdateAll()
    return {"layers": len(layers)}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def scaled(record, ratio):
    """Scale a guide's x by `ratio` (advance-width ratio); an angled guide keeps its direction on screen."""
    x, y, angle, name = record
    if angle == 0:
        return record
    if angle == 90:
        return (round(x * ratio, 2), y, angle, name)
    radians = math.radians(angle)
    angle = math.degrees(math.atan2(math.sin(radians), math.cos(radians) * ratio)) % 180
    return (round(x * ratio, 2), y, round(angle, 2), name)


def target_records(source, target, replace, follow_width):
    """The guide records the target layer should end with; None when the widths make scaling impossible."""
    ratio = 1.0
    if follow_width:
        if source.advanceWidth <= 0 or target.advanceWidth <= 0:
            return None
        ratio = target.advanceWidth / float(source.advanceWidth)
    copied = [scaled(guide_record(g), ratio) for g in glyph_guides(source)]
    if replace:
        return copied
    existing = [guide_record(g) for g in glyph_guides(target)]
    return existing + [r for r in copied if r not in existing]


class CopyGuides(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(560)
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
        self.source = QtGui.QComboBox()
        self.source.addItems(self.masters)
        if self.current_master in self.masters:
            self.source.setCurrentIndex(self.masters.index(self.current_master))
        targets = QtGui.QGridLayout()
        targets.setHorizontalSpacing(14)
        self.target_checks = {}
        for index, master in enumerate(self.masters):
            check = QtGui.QCheckBox(master)
            check.setChecked(True)
            self.target_checks[master] = check
            targets.addWidget(check, index // 3, index % 3)
        self.mode = QtGui.QComboBox()
        self.mode.addItems(["Add to the target guides", "Replace the target guides"])
        self.follow_width = QtGui.QCheckBox("Scale x positions by the advance-width ratio")
        self.follow_width.setChecked(True)
        form.addWidget(QtGui.QLabel("From"), 0, 0)
        form.addWidget(self.source, 0, 1)
        form.addWidget(QtGui.QLabel("To"), 1, 0, QtCore.Qt.AlignTop)
        form.addLayout(targets, 1, 1)
        form.addWidget(QtGui.QLabel("Mode"), 2, 0)
        form.addWidget(self.mode, 2, 1)
        form.addWidget(self.follow_width, 3, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Glyph · master", "Guide", "Position", "Action"])
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
        self.apply_button = QtGui.QPushButton("Copy")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.source.currentIndexChanged, lambda *a: self.refresh())
        for check in self.target_checks.values():
            self._connect(check.toggled, lambda *a: self.refresh())
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.follow_width.toggled, lambda *a: self.refresh())
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
    def targets(self):
        source = self.source.currentText
        return [m for m in self.masters if m != source and self.target_checks[m].isChecked()]

    def plan(self):
        """[(glyph, master, layer, old records, new records or None, note)]."""
        planned = []
        source_master = self.source.currentText
        for glyph in self.glyphs:
            source = glyph.findLayer(source_master)
            if source is None or source.isNull:
                continue
            for master, layer in master_layers(glyph, self.targets()):
                old = [guide_record(g) for g in glyph_guides(layer)]
                if layer.autoLayer:
                    planned.append((glyph, master, layer, old, None, "auto layer, skipped"))
                    continue
                new = target_records(source, layer, self.mode.currentIndex == 1, self.follow_width.isChecked())
                note = "zero advance width, skipped" if new is None else ""
                planned.append((glyph, master, layer, old, new, note))
        return planned

    def refresh(self):
        for master, check in self.target_checks.items():
            check.setEnabled(master != self.source.currentText)
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (" …" if count > 8 else "")
            self.subtitle.setText(f"Copies glyph guides in {count} glyph{'s' if count != 1 else ''}: {names}")
        rows, changes = [], 0
        for glyph, master, layer, old, new, note in (self.plan() if self.glyphs else []):
            label = f"{glyph.name} · {master}"
            if new is None:
                rows.append((label, note, "", ""))
                continue
            for record in old:
                if record not in new:
                    rows.append((label, record[3] or "(unnamed)", self.position(record), "remove"))
            for record in new:
                if record not in old:
                    rows.append((label, record[3] or "(unnamed)", self.position(record), "add"))
            if new != old:
                changes += 1
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
        self.apply_button.setEnabled(changes > 0)
        self.status.setText(f"{changes} layer{'s' if changes != 1 else ''} to change")

    def position(self, record):
        x, y, angle, _ = record
        return f"y {y:g}" if angle == 0 else f"x {x:g}" if angle == 90 else f"{x:g}, {y:g} · {angle:g}°"

    def apply(self):
        jobs = [(glyph, layer, new) for glyph, master, layer, old, new, note in self.plan()
                if new is not None and new != old]
        self.last_result = replace_guides(jobs)
        self.refresh()
        self.status.setText(f"Copied guides to {self.last_result['layers']} layers")

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
    dialog = CopyGuides(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
