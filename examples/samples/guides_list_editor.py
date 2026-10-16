#FLM: Guides · Guide List Editor
# this_file: samples/guides_list_editor.py
"""Edit the glyph guides of one glyph as a table: X, Y, angle and name per master.

Change cells, add or delete rows, then Apply: each master's guides become exactly
the rows listed for it. Unchanged guides keep their style. Auto layers are shown
but not edited. One Apply is one Undo step.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Guide List Editor"
KEY = "guides_list_editor"
COLUMNS = ["Master", "X", "Y", "Angle °", "Name"]


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


def parse_row(cells, row):
    """(master, (x, y, angle, name)) from the table's text cells; raises ValueError with the row number."""
    master, x, y, angle, name = cells
    try:
        x, y, angle = float(x or 0), float(y or 0), float(angle or 0) % 180
    except ValueError:
        raise ValueError(f"row {row + 1}: X, Y and angle must be numbers")
    if angle == 0:
        x = 0.0
    elif angle == 90:
        y = 0.0
    return master, (round(x, 2), round(y, 2), round(angle, 2), name.strip())


class ListEditor(QtGui.QDialog):
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
        glyphs = selected_glyphs(self.package) if self.package else []
        self.glyph = glyphs[0] if glyphs else None
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
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Masters"), 0, 0)
        form.addWidget(self.scope, 0, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(220)
        root.addWidget(self.table, 1)

        rows = QtGui.QHBoxLayout()
        self.add_button = QtGui.QPushButton("Add guide")
        self.delete_button = QtGui.QPushButton("Delete selected")
        self.reload_button = QtGui.QPushButton("Revert")
        rows.addWidget(self.add_button)
        rows.addWidget(self.delete_button)
        rows.addStretch(1)
        rows.addWidget(self.reload_button)
        root.addLayout(rows)

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

        self._connect(self.scope.currentIndexChanged, lambda *a: self.reload())
        self._connect(self.add_button.clicked, lambda *a: self.add_row())
        self._connect(self.delete_button.clicked, lambda *a: self.delete_row())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.reload()

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

    def layers(self):
        return master_layers(self.glyph, self.chosen_masters()) if self.glyph else []

    def editable_masters(self):
        return [m for m, layer in self.layers() if not layer.autoLayer]

    def set_row(self, row, master, values):
        ink = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        x, y, angle, name = values
        for column, text in enumerate([master, f"{x:g}", f"{y:g}", f"{angle:g}", name]):
            item = QtGui.QTableWidgetItem(text)
            item.setForeground(QtGui.QBrush(ink))
            if column == 0:
                item.setFlags(int(item.flags()) & ~int(QtCore.Qt.ItemIsEditable))
            elif column < 4:
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
            self.table.setItem(row, column, item)

    def reload(self):
        """Fill the table from the font (discards unapplied edits)."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif self.glyph is None:
            self.subtitle.setText("Select a glyph in the Font window, then run this script again.")
        else:
            skipped = [m for m, layer in self.layers() if layer.autoLayer]
            note = f" · auto layer{'s' if len(skipped) != 1 else ''} not editable: {', '.join(skipped)}" if skipped else ""
            self.subtitle.setText(f"Glyph guides of {self.glyph.name}; Apply makes each master match its rows{note}")
        rows = [(m, guide_record(g)) for m, layer in self.layers() if not layer.autoLayer for g in glyph_guides(layer)]
        self.table.setRowCount(len(rows))
        for row, (master, values) in enumerate(rows):
            self.set_row(row, master, values)
        self.apply_button.setEnabled(bool(self.editable_masters()))
        self.status.setText(f"{len(rows)} guide{'s' if len(rows) != 1 else ''}")

    def add_row(self):
        masters = self.editable_masters()
        if not masters:
            return
        master = self.current_master if self.current_master in masters else masters[0]
        row = self.table.rowCount
        self.table.setRowCount(row + 1)
        self.set_row(row, master, (0.0, 0.0, 0.0, "new guide"))
        self.table.setCurrentCell(row, 2)

    def delete_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def table_records(self):
        """{master: [records]} from the table, in row order."""
        records = {m: [] for m in self.editable_masters()}
        for row in range(self.table.rowCount):
            cells = [self.table.item(row, c).text() if self.table.item(row, c) else "" for c in range(len(COLUMNS))]
            master, values = parse_row(cells, row)
            if master in records:
                records[master].append(values)
        return records

    def apply(self):
        wanted = self.table_records()
        jobs = []
        for master, layer in self.layers():
            if master in wanted and [guide_record(g) for g in glyph_guides(layer)] != wanted[master]:
                jobs.append((self.glyph, layer, wanted[master]))
        self.last_result = replace_guides(jobs)
        self.reload()
        self.status.setText(f"Updated guides on {self.last_result['layers']} master{'s' if self.last_result['layers'] != 1 else ''}")

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
    dialog = ListEditor(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
