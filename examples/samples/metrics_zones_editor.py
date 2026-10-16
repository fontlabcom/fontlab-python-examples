#FLM: Metrics · Alignment Zones
# this_file: samples/metrics_zones_editor.py
"""Edit the PostScript alignment zones (blue zones) of each master in a table.

Pick a master, add, remove or edit top and bottom zones, or let "Suggest" measure the overshoots
of o and O against the baseline, x-height and cap height of that master. Edits are kept per
master until Apply, which writes every changed master as one Undo step and returns to the
master you were on. Top zones extend up from their position, bottom zones down.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Alignment Zones"
KEY = "metrics_zones_editor"
KINDS = ["Top", "Bottom"]


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def zone_tuples(zones):
    return [(round(z.position), round(z.width), z.name or "") for z in zones]


def read_zones(package):
    """{master: {"Top": [(pos, width, name)], "Bottom": [...], "metrics": {...}}}, current master restored."""
    start, out = package.master, {}
    try:
        for master in list(package.masters):
            package.setMaster(master)
            package.updateZonesFromGuidelines()  # FontLab keeps PS zones as zone guidelines
            out[master] = {
                "Top": zone_tuples(package.ps_zonesT),
                "Bottom": zone_tuples(package.ps_zonesB),
                "metrics": {"xHeight": package.xHeight_value, "capsHeight": package.capsHeight_value},
            }
    finally:
        package.setMaster(start)
    return out


# ---------------------------------------------------------------- core
def vertical_extent(package, name, master):
    glyph = package.findName(name)
    layer = glyph.findLayer(master) if glyph is not None else None
    if layer is None or layer.isNull:
        return None
    box = layer.boundingBox
    if box.height() <= 0:
        return None
    return box.y(), box.y() + box.height()


def suggest(package, master, metrics):
    """Zones from o/O overshoots: baseline (bottom), x-height and cap height (top)."""
    top, bottom = [], []
    lower, upper = vertical_extent(package, "o", master), vertical_extent(package, "O", master)
    under = [-e[0] for e in (lower, upper) if e is not None and e[0] < 0]
    if under:
        bottom.append((0, round(max(under)), "baseline"))
    if lower is not None and lower[1] > metrics["xHeight"]:
        top.append((round(metrics["xHeight"]), round(lower[1] - metrics["xHeight"]), "x-height"))
    if upper is not None and upper[1] > metrics["capsHeight"]:
        top.append((round(metrics["capsHeight"]), round(upper[1] - metrics["capsHeight"]), "cap height"))
    return {"Top": top, "Bottom": bottom}


def changed_masters(original, edited):
    return [m for m in edited if (edited[m]["Top"], edited[m]["Bottom"]) != (original[m]["Top"], original[m]["Bottom"])]


def run(package, edited, masters):
    """Write the zones of `masters` as one Undo step; the current master is restored."""
    if not masters:
        return {"masters": 0}
    items = [package, package.mastersContainer()]
    start = package.master
    package.checkInitHistoryState(0)
    fontlab.flItems.notifyChangesApplied(TITLE, items)
    try:
        for master in masters:
            package.setMaster(master)
            top = [fontlab.flZone(p, w, n) for p, w, n in sorted(edited[master]["Top"])]
            bottom = [fontlab.flZone(p, w, n) for p, w, n in sorted(edited[master]["Bottom"])]
            # Zones live in the master's zone guidelines; ps_zonesT/B is only a cache of them.
            package.convertZonesToGuidelines(top, bottom)
            package.updateZonesFromGuidelines()
    finally:
        package.setMaster(start)
    fontlab.flItems.notifyChangesApplied(TITLE, items)
    return {"masters": len(masters)}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class ZonesEditor(QtGui.QDialog):
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
        self.original = read_zones(self.package) if self.package else {}
        self.edited = {m: {"Top": list(v["Top"]), "Bottom": list(v["Bottom"])} for m, v in self.original.items()}
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
        form.addWidget(QtGui.QLabel("Master"))
        self.master = QtGui.QComboBox()
        for name in self.masters:
            self.master.addItem(name)
        if self.current_master in self.masters:
            self.master.setCurrentIndex(self.masters.index(self.current_master))
        form.addWidget(self.master, 1)
        self.suggest_button = QtGui.QPushButton("Suggest from o / O")
        form.addWidget(self.suggest_button)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Zone", "Position", "Width", "Name"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(200)
        root.addWidget(self.table, 1)

        edits = QtGui.QHBoxLayout()
        self.add_top = QtGui.QPushButton("Add top zone")
        self.add_bottom = QtGui.QPushButton("Add bottom zone")
        self.remove_button = QtGui.QPushButton("Remove selected")
        edits.addWidget(self.add_top)
        edits.addWidget(self.add_bottom)
        edits.addWidget(self.remove_button)
        edits.addStretch(1)
        root.addLayout(edits)

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

        self._connect(self.master.currentIndexChanged, lambda *a: self.fill())
        self._connect(self.table.itemChanged, lambda *a: self.read_table())
        self._connect(self.suggest_button.clicked, lambda *a: self.suggest())
        self._connect(self.add_top.clicked, lambda *a: self.add("Top"))
        self._connect(self.add_bottom.clicked, lambda *a: self.add("Bottom"))
        self._connect(self.remove_button.clicked, lambda *a: self.remove_selected())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.fill()

    def _connect(self, signal, slot):
        def guarded(*args):
            # An exception escaping a PythonQt slot can take FontLab down: report it instead.
            try:
                return slot(*args)
            except Exception as error:
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def chosen_master(self):
        return self.masters[self.master.currentIndex] if self.masters else ""

    def fill(self):
        """Show the chosen master's staged zones; top zones first, each kind sorted by position."""
        master = self.chosen_master()
        rows = []
        if master:
            rows = [("Top",) + z for z in sorted(self.edited[master]["Top"], reverse=True)]
            rows += [("Bottom",) + z for z in sorted(self.edited[master]["Bottom"], reverse=True)]
        self.filling = True
        self.table.setRowCount(len(rows))
        for row, (kind, position, width, name) in enumerate(rows):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(kind))
            for column, value in ((1, position), (2, width)):
                item = QtGui.QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, value)
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
            self.table.setItem(row, 3, QtGui.QTableWidgetItem(name))
        self.filling = False
        self.refresh()

    def read_table(self):
        """Store the edited table back into the chosen master's staged zones."""
        if self.filling:
            return
        zones = {"Top": [], "Bottom": []}
        for row in range(self.table.rowCount):
            kind = "Bottom" if self.table.item(row, 0).text().strip().lower().startswith("b") else "Top"
            try:
                position = int(round(float(self.table.item(row, 1).text())))
                width = int(round(float(self.table.item(row, 2).text())))
            except ValueError:
                continue
            name = self.table.item(row, 3).text() if self.table.item(row, 3) is not None else ""
            zones[kind].append((position, abs(width), name))
        self.edited[self.chosen_master()] = zones
        self.refresh()

    def add(self, kind):
        master = self.chosen_master()
        metrics = self.original[master]["metrics"]
        position = round(metrics["xHeight"]) if kind == "Top" else 0
        self.edited[master][kind].append((position, 12, ""))
        self.fill()

    def remove_selected(self):
        rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()}, reverse=True)
        for row in rows:
            self.table.removeRow(row)
        self.read_table()

    def suggest(self):
        master = self.chosen_master()
        self.edited[master] = suggest(self.package, master, self.original[master]["metrics"])
        self.fill()

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            self.subtitle.setText("PostScript alignment zones per master. Top zones extend up from their position, "
                                  "bottom zones down.")
        pending = changed_masters(self.original, self.edited)
        master = self.chosen_master()
        count = len(self.edited[master]["Top"]) + len(self.edited[master]["Bottom"]) if master else 0
        note = f" · unsaved: {', '.join(pending)}" if pending else ""
        self.status.setText(f"{master}: {count} zone{'s' if count != 1 else ''}{note}")
        self.apply_button.setEnabled(bool(pending))
        self.remove_button.setEnabled(self.table.rowCount > 0)

    def apply(self):
        pending = changed_masters(self.original, self.edited)
        result = run(self.package, self.edited, pending)
        self.last_result = result
        fontlab.UpdateAll()
        self.original = read_zones(self.package)
        self.edited = {m: {"Top": list(v["Top"]), "Bottom": list(v["Bottom"])} for m, v in self.original.items()}
        self.fill()
        self.status.setText(f"Wrote the zones of {result['masters']} master{'s' if result['masters'] != 1 else ''}")

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
    dialog = ZonesEditor(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
