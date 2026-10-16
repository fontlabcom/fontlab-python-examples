#FLM: Hinting · Suggest Zones from Overshoots
# this_file: samples/zones_from_glyphs.py
"""Set PostScript alignment zones from the overshoots of H/O (baseline, caps) and x/o (x-height).

For each master the zone sits at the flat glyph's edge (H, x) and is as wide as the round
glyph's overshoot (O, o): top zones extend up, the baseline zone down. A zone already at
that position, or with the same name, is replaced and keeps its name; other zones stay.
The glyphs are only measured, never changed.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = 'Suggest Zones from Overshoots'
KEY = "zones_from_glyphs"


def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def selected_glyphs(package, all_glyphs=False):
    import FL

    font = FL.fl.font
    names = [font[i].name for i in range(len(font))
             if all_glyphs or FL.fl.Selected(i)]
    if not names and not all_glyphs:
        glyph = fontlab.CurrentGlyph()
        names = [glyph.name] if glyph is not None else []
    return [package.findName(name) for name in names]


def master_layers(glyphs, masters):
    return [(glyph, master, layer) for glyph in glyphs for master in masters
            for layer in [glyph.findLayer(master)]
            if layer is not None and not layer.isNull]


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
    color.setAlpha(160)
    return color.name(QtGui.QColor.HexArgb)


def overshoot_zone(flat, curved, top):
    position = round(flat)
    width = max(0, round(curved - flat if top else flat - curved))
    return position, width


def suggestions(package, masters):
    rows = []
    for master in masters:
        for name, flat_name, round_name, top in [("baseline", "H", "O", False),
                                                ("x-height", "x", "o", True),
                                                ("caps", "H", "O", True)]:
            pair = []
            for glyph_name in (flat_name, round_name):
                glyph = package.findName(glyph_name)
                layer = glyph.findLayer(master) if glyph is not None and not glyph.isNull else None
                if layer is None or layer.isNull or not layer.getContours():
                    break
                box = layer.boundingBox
                pair.append(box.y() + box.height() if top else box.y())
            if len(pair) == 2:
                position, width = overshoot_zone(*pair, top)
                rows.append((master, name, position, width, top))
    return rows


def zone_lists(package, master):
    """{True: top zones, False: bottom zones} of one master (switches the current master).

    FontLab keeps PS zones as the master's zone guidelines; ps_zonesT/B is a cache refreshed from them."""
    package.setMaster(master)
    package.updateZonesFromGuidelines()
    return {True: list(package.ps_zonesT), False: list(package.ps_zonesB)}


def replaced(zones, name, position):
    """The existing zone this suggestion replaces: same position, else same name; None to add."""
    same_place = [z for z in zones if round(z.position) == position]
    same_name = [z for z in zones if z.name == name]
    return (same_place or same_name or [None])[0]


def with_current(package, rows):
    """rows + the zone each one replaces, read per master; the original master is restored."""
    original = package.master
    out = []
    try:
        for master in dict.fromkeys(r[0] for r in rows):
            zones = zone_lists(package, master)
            for row in [r for r in rows if r[0] == master]:
                out.append(row + (replaced(zones[row[4]], row[1], row[2]),))
    finally:
        package.setMaster(original)
    return out


def run(package, masters):
    rows = suggestions(package, masters)
    original = package.master
    objects = [package, package.mastersContainer()]
    if rows:
        package.checkInitHistoryState(0)
        fontlab.flItems().notifyChangesApplied(TITLE, objects)
        try:
            for master in masters:
                proposed = [r for r in rows if r[0] == master]
                if not proposed:
                    continue
                zones = zone_lists(package, master)
                for _, name, position, width, top in proposed:
                    old = replaced(zones[top], name, position)
                    if old is not None:
                        zones[top].remove(old)
                        name = old.name or name
                    zones[top].append(fontlab.flZone(position, width, name))
                # Writing ps_zonesT/B alone never reaches the saved master (measured): write the guidelines.
                package.convertZonesToGuidelines(zones[True], zones[False])
                package.updateZonesFromGuidelines()
        finally:
            package.setMaster(original)
            fontlab.flItems().notifyChangesApplied(TITLE, objects)
            fontlab.UpdateAll()
    return {"zones": len(rows), "rows": rows}


class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self.setMinimumWidth(620)
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
        face = heading.font
        face.setPointSizeF(face.pointSizeF() * 1.35)
        face.setBold(True)
        heading.setFont(face)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel('Zones at the flat edges of H and x, as wide as the overshoots of O and o. A zone at the same position is replaced; other zones stay.')
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        form = QtGui.QFormLayout()
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addRow("Masters", self.scope)
        root.addLayout(form)
        self.table = QtGui.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['Master', 'Zone', 'Position', 'Width', 'Replaces'])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setShowGrid(False)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(250)
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton('Apply')
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())

        self._safe(self.refresh)

    def _safe(self, callback):
        try:
            callback()
        except Exception as error:
            self.status.setText(f"{type(error).__name__}: {error}")
            self.apply_button.setEnabled(False)

    def _connect(self, signal, slot):
        guarded = lambda *a: self._safe(lambda: slot(*a))
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def chosen_masters(self):
        return self.masters if self.scope.currentIndex else [self.current_master]

    def show_rows(self, rows, enabled=True):
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, value in enumerate(cells):
                item = QtGui.QTableWidgetItem(str(value))
                if column in (2, 3):
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
        self.apply_button.setEnabled(bool(rows) and enabled)
        self.status.setText(f"{len(rows)} zone{'s' if len(rows) != 1 else ''} · measured from H, O, x, o")
        if self.package is None:
            self.subtitle.setText("Open a font, then run this script again.")

    def refresh(self):
        rows = with_current(self.package, suggestions(self.package, self.chosen_masters())) if self.package else []
        self.show_rows([(m, n, p, f"+{w}" if top else f"-{w}",
                         f"{old.name or '(unnamed)'} · {round(old.position)}, {round(old.width)}" if old else "— (new)")
                        for m, n, p, w, top, old in rows])

    def apply(self):
        self.last_result = run(self.package, self.chosen_masters())
        self.refresh()
        self.status.setText(f"Set {self.last_result['zones']} zones")

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        windows = getattr(sys, "_fontlab_samples", {})
        if windows.get(KEY) is self:
            windows.pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


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
