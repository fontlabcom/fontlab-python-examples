#FLM: Metrics · Sidebearings Tuner
# this_file: samples/metrics_sidebearings_tuner.py
"""Set, add to or scale the side-bearings of the selected glyphs on one or all masters.

A table previews current and resulting LSB/RSB per glyph and master before
anything changes. One Apply is one Undo step. Auto layers (composites that
FontLab rebuilds itself) are listed but not edited.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Sidebearings Tuner"
KEY = "metrics_sidebearings_tuner"


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
    """{master: flLayer} for the masters present in this glyph."""
    found = {}
    for master in masters:
        layer = glyph.findLayer(master)
        if layer is not None and not layer.isNull:
            found[master] = layer
    return found


# ---------------------------------------------------------------- core
def bounds(layer):
    box = layer.boundingBox
    if box.width() <= 0 and box.height() <= 0:
        return None
    return box.x(), box.x() + box.width()


def sidebearings(layer):
    """(lsb, rsb) or None for an empty layer."""
    edges = bounds(layer)
    if edges is None:
        return None
    left, right = edges
    return left, layer.advanceWidth - right


def target_value(mode, current, value):
    if mode == "set":
        return value
    if mode == "add":
        return current + value
    return current * value / 100.0


def plan(layer, mode, lsb_value, rsb_value, do_lsb, do_rsb):
    """(lsb, rsb, new_lsb, new_rsb) rounded to units, or None when the layer is empty."""
    current = sidebearings(layer)
    if current is None:
        return None
    lsb, rsb = current
    new_lsb = round(target_value(mode, lsb, lsb_value)) if do_lsb else round(lsb)
    new_rsb = round(target_value(mode, rsb, rsb_value)) if do_rsb else round(rsb)
    return round(lsb), round(rsb), new_lsb, new_rsb


def apply_layer(layer, new_lsb, new_rsb):
    """Shift the outline so LSB == new_lsb, then set the advance for RSB == new_rsb."""
    left, right = bounds(layer)
    dx = new_lsb - left
    if dx:
        layer.applyTransform(QtGui.QTransform(1, 0, 0, 1, dx, 0))
    layer.advanceWidth = round(right + dx + new_rsb)


def run(glyphs, masters, mode, lsb_value, rsb_value, do_lsb=True, do_rsb=True):
    """Apply to every editable layer; one Undo step. Returns a summary dict."""
    changed_layers, changed_glyphs, skipped = [], [], []
    for glyph in glyphs:
        touched = False
        for master, layer in master_layers(glyph, masters).items():
            if layer.autoLayer:
                skipped.append(f"{glyph.name}/{master} (auto layer)")
                continue
            values = plan(layer, mode, lsb_value, rsb_value, do_lsb, do_rsb)
            if values is None:
                continue
            lsb, rsb, new_lsb, new_rsb = values
            if (lsb, rsb) == (new_lsb, new_rsb):
                continue
            apply_layer(layer, new_lsb, new_rsb)
            changed_layers.append(layer)
            touched = True
        if touched:
            changed_glyphs.append(glyph)
    if changed_layers:
        fontlab.flItems().notifyChangesApplied(TITLE, changed_layers + changed_glyphs)
    return {"layers": len(changed_layers), "glyphs": len(changed_glyphs), "skipped": skipped}


# ---------------------------------------------------------------- GUI
def auto_dependants(package, names):
    """Auto composites (any auto master layer) that use one of `names` as a component."""
    wanted = set(names)
    if package is None or not wanted:
        return []
    import FL

    font, found = FL.fl.font, []
    for index in range(len(font)):
        glyph = package.findName(font[index].name)
        if glyph is None or glyph.name in wanted:
            continue
        for layer in glyph.layers:
            if layer.isMasterLayer and layer.autoLayer and any(
                    shape.isComponent and str(shape.shapeData.componentGlyph) in wanted for shape in layer.shapes):
                found.append(glyph.name)
                break
    return found


def rebuild_note(package, names, limit=5):
    """Status text naming the auto composites FontLab rebuilds when their bases are notified (fl#8512)."""
    found = auto_dependants(package, names)
    if not found:
        return ""
    shown = ", ".join(found[:limit]) + (f" +{len(found) - limit} more" if len(found) > limit else "")
    return f"FontLab will rebuild auto {shown} (anchors/locks may change; Undo does not restore them)"


def show_rebuilds(dialog, names):
    """Append the auto composites FontLab will rebuild to the dialog's status: notifying a base of
    auto composites re-resolves auto layers font-wide (AGENTS: editing a BASE of auto composites)."""
    status = getattr(dialog, "status", None)
    note = rebuild_note(dialog.package, names) if status is not None else ""
    if note:
        text = status.text
        status.setText(f"{text} · {note}" if text else note)
        # the wrapped note must not overlap the table: reserve its height, which grows the dialog
        status.setMinimumHeight(status.heightForWidth(max(status.width, 320)))


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Tuner(QtGui.QDialog):
    MODES = [("Set to", "set"), ("Add", "add"), ("Scale %", "scale")]

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(520)
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
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
        self.mode = QtGui.QComboBox()
        for label, _ in self.MODES:
            self.mode.addItem(label)
        self.lsb_check = QtGui.QCheckBox("LSB")
        self.lsb_check.setChecked(True)
        self.rsb_check = QtGui.QCheckBox("RSB")
        self.rsb_check.setChecked(True)
        self.lsb = self._spin()
        self.rsb = self._spin()
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Operation"), 0, 0)
        form.addWidget(self.mode, 0, 1, 1, 3)
        form.addWidget(self.lsb_check, 1, 0)
        form.addWidget(self.lsb, 1, 1)
        form.addWidget(self.rsb_check, 1, 2)
        form.addWidget(self.rsb, 1, 3)
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Glyph · master", "LSB", "RSB", "New LSB", "New RSB"])
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
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.mode.currentIndexChanged, lambda *a: self.mode_changed())
        for widget in (self.lsb, self.rsb):
            self._connect(widget.valueChanged, lambda *a: self.refresh())
        for widget in (self.lsb_check, self.rsb_check):
            self._connect(widget.toggled, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.mode_changed()

    def _spin(self):
        spin = QtGui.QSpinBox()
        spin.setRange(-2000, 2000)
        spin.setAlignment(QtCore.Qt.AlignRight)
        return spin

    def _connect(self, signal, slot):
        signal.connect(slot)
        self._connections.append((signal, slot))

    # state
    def mode_key(self):
        return self.MODES[self.mode.currentIndex][1]

    def chosen_masters(self):
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def mode_changed(self):
        scale = self.mode_key() == "scale"
        for spin in (self.lsb, self.rsb):
            spin.setSuffix(" %" if scale else "")
            if scale and spin.value == 0:
                spin.setValue(100)
            if not scale and spin.value == 100:
                spin.setValue(0)
        self.refresh()

    def refresh(self):
        self.refresh_listing()
        show_rebuilds(self, [g.name for g in self.glyphs])

    def refresh_listing(self):
        self.lsb.setEnabled(self.lsb_check.isChecked())
        self.rsb.setEnabled(self.rsb_check.isChecked())
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (" …" if count > 8 else "")
            self.subtitle.setText(f"{count} glyph{'s' if count != 1 else ''}: {names}")
        rows = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()).items():
                if layer.autoLayer:
                    rows.append((f"{glyph.name} · {master}", "auto layer", "", "skipped", ""))
                    continue
                values = plan(layer, self.mode_key(), self.lsb.value, self.rsb.value,
                              self.lsb_check.isChecked(), self.rsb_check.isChecked())
                if values is None:
                    rows.append((f"{glyph.name} · {master}", "–", "–", "empty", ""))
                    continue
                lsb, rsb, new_lsb, new_rsb = values
                rows.append((f"{glyph.name} · {master}", str(lsb), str(rsb), str(new_lsb), str(new_rsb)))
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if column >= 3 and text != cells[column - 2]:
                    bold = item.font()
                    bold.setBold(True)
                    item.setFont(bold)
                    item.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, column, item)
        self.apply_button.setEnabled(bool(rows))
        self.status.setText(f"{len(rows)} layer{'s' if len(rows) != 1 else ''} in preview")

    def apply(self):
        result = run(self.glyphs, self.chosen_masters(), self.mode_key(), self.lsb.value,
                     self.rsb.value, self.lsb_check.isChecked(), self.rsb_check.isChecked())
        self.last_result = result
        fontlab.UpdateAll()
        self.refresh()
        note = f" · {len(result['skipped'])} auto layers skipped" if result["skipped"] else ""
        self.status.setText(f"Changed {result['layers']} layers in {result['glyphs']} glyphs{note}")

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
    dialog = Tuner(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
