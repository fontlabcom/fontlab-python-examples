#FLM: Guides · Clear Glyph Guides
# this_file: samples/guides_clear.py
"""Remove glyph guides from the selected glyphs by direction and name.

The table lists exactly the guides that will go. Hints and font-wide guides are
not touched; auto layers are skipped. One Apply is one Undo step.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Clear Glyph Guides"
KEY = "guides_clear"
DIRECTIONS = ["Any direction", "Horizontal", "Vertical", "Angled"]


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


def direction_of(record):
    angle = record[2]
    return "Horizontal" if angle == 0 else "Vertical" if angle == 90 else "Angled"


def matches(record, direction, text):
    """True when the guide fits the direction filter and its name contains `text` (case-insensitive)."""
    if direction != DIRECTIONS[0] and direction_of(record) != direction:
        return False
    return not text or text.lower() in record[3].lower()


def rewrite_guides(layer, keep):
    """Remove all glyph guides of the layer, then put back copies of the `keep` guides."""
    kept = [(guide_record(g), fontlab.flGuideLine(g)) for g in keep]  # read before the originals go
    layer.removeGuides(True, True)
    left = [guide_record(g) for g in glyph_guides(layer)]  # what removeGuides did not remove
    restore = []
    for record, copy in kept:
        if record in left:
            left.remove(record)
        else:
            restore.append(copy)
    if restore:
        layer.appendGuidelines(restore)


def clear(jobs):
    """jobs: [(glyph, layer, [guides to keep])]. Notify before and after: one Undo step."""
    layers = [layer for _, layer, _ in jobs]
    glyphs = []
    for glyph, _, _ in jobs:
        if glyph not in glyphs:
            glyphs.append(glyph)
    if not layers:
        return {"layers": 0, "removed": 0, "left": 0}
    before = sum(len(glyph_guides(layer)) for layer in layers)
    items = layers + glyphs
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    for _, layer, keep in jobs:
        rewrite_guides(layer, keep)
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    fontlab.UpdateAll()
    after = sum(len(glyph_guides(layer)) for layer in layers)
    expected = sum(len(keep) for _, _, keep in jobs)
    return {"layers": len(layers), "removed": before - after, "left": after - expected}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class ClearGuides(QtGui.QDialog):
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
        self.direction = QtGui.QComboBox()
        self.direction.addItems(DIRECTIONS)
        self.name_filter = QtGui.QLineEdit()
        self.name_filter.setPlaceholderText("any name")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Direction"), 0, 0)
        form.addWidget(self.direction, 0, 1)
        form.addWidget(QtGui.QLabel("Name contains"), 1, 0)
        form.addWidget(self.name_filter, 1, 1)
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Glyph · master", "Guide", "Direction", "Position"])
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
        self.apply_button = QtGui.QPushButton("Remove")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.direction.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.name_filter.textChanged, lambda *a: self.refresh())
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
        """[(glyph, master, layer, [guides to remove], [guides to keep])]."""
        direction, text = self.direction.currentText, self.name_filter.text
        planned = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()):
                guides = glyph_guides(layer)
                remove = [g for g in guides if matches(guide_record(g), direction, text)]
                keep = [g for g in guides if g not in remove]
                planned.append((glyph, master, layer, remove, keep))
        return planned

    def refresh(self):
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (" …" if count > 8 else "")
            self.subtitle.setText(f"Removes matching glyph guides from {count} glyph{'s' if count != 1 else ''}: {names}")
        rows = []
        for glyph, master, layer, remove, keep in (self.plan() if self.glyphs else []):
            if layer.autoLayer:
                if remove:
                    rows.append((f"{glyph.name} · {master}", "auto layer, skipped", "", ""))
                continue
            for guide in remove:
                x, y, angle, name = guide_record(guide)
                kind = direction_of((x, y, angle, name))
                position = f"{y:g}" if kind == "Horizontal" else f"{x:g}" if kind == "Vertical" else f"{x:g}, {y:g} · {angle:g}°"
                rows.append((f"{glyph.name} · {master}", name or "(unnamed)", kind, position))
        ink = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(QtGui.QBrush(ink))
                if column == 3:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
        removable = sum(1 for cells in rows if cells[1] != "auto layer, skipped")
        self.apply_button.setEnabled(removable > 0)
        self.status.setText(f"{removable} guide{'s' if removable != 1 else ''} to remove")

    def apply(self):
        jobs = [(glyph, layer, keep) for glyph, master, layer, remove, keep in self.plan()
                if remove and not layer.autoLayer]
        self.last_result = clear(jobs)
        self.refresh()
        note = f" · {self.last_result['left']} could not be removed" if self.last_result["left"] else ""
        self.status.setText(f"Removed {self.last_result['removed']} guides from {self.last_result['layers']} layers{note}")

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
    dialog = ClearGuides(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
