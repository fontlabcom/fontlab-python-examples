#FLM: Metrics · Italic Sidebearings
# this_file: samples/metrics_italic_sidebearings.py
"""Report and set sidebearings measured along the italic angle, not straight up.

In a slanted design the plain LSB/RSB depend on the overhangs of the slant; italic sidebearings
de-slant the outline around a height (half the x-height by default) first, so an italic "n" and
"o" can be compared like upright ones. The table shows both; Set/Add edits the italic values.
One Apply is one Undo step; auto layers are skipped.

Edit > Undo restores outlines, anchors and advances. Stem hints that moved with the outline
keep their new positions after Undo: FontLab does not restore them (measured natively).
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Italic Sidebearings"
KEY = "metrics_italic_sidebearings"
MODES = [("Add to italic sidebearings", "add"), ("Set italic sidebearings to", "set")]


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
def outline(layer):
    """The layer's outline as one QPainterPath, components placed by their transforms."""
    path = QtGui.QPainterPath()
    for shape in layer.shapes:
        part = QtGui.QPainterPath()
        for contour in shape.getContours():
            part.addPath(contour.path())
        path.addPath(shape.transform.map(part))
    return path


def deslant(angle, pivot):
    """QTransform that undoes a slant of `angle` degrees (FontLab sign) around y = pivot."""
    slope = math.tan(math.radians(angle))
    return QtGui.QTransform(1, 0, slope, 1, -pivot * slope, 0)


def italic_sidebearings(layer, angle, pivot):
    """(italic lsb, italic rsb) as floats, or None for an empty layer."""
    path = outline(layer)
    if path.isEmpty():
        return None
    box = deslant(angle, pivot).map(path).boundingRect()
    return box.x(), layer.advanceWidth - (box.x() + box.width())


def plan(layer, angle, pivot, mode, lsb_value, rsb_value, do_lsb, do_rsb):
    """(ilsb, irsb, new_ilsb, new_irsb, dx, new_width) or None when the layer is empty."""
    values = italic_sidebearings(layer, angle, pivot)
    if values is None:
        return None
    ilsb, irsb = values
    new_ilsb = (ilsb + lsb_value if mode == "add" else lsb_value) if do_lsb else ilsb
    new_irsb = (irsb + rsb_value if mode == "add" else rsb_value) if do_rsb else irsb
    dx = round(new_ilsb - ilsb)
    new_width = round(layer.advanceWidth + dx + (new_irsb - irsb))
    return ilsb, irsb, ilsb + dx, new_width - layer.advanceWidth - dx + irsb, dx, new_width


def detach_shapes(layer):
    """Swap fresh clones in for the layer's shapes before moving them.

    FontLab's Undo history keeps references to the shapes themselves, so moving the
    attached originals would change the stored state too and Undo could not restore it.
    """
    for index, shape in enumerate(list(layer.shapes)):
        clone = shape.clone()
        layer.removeShape(shape)
        layer.insertShape(index, clone)


def shift_and_set(layer, dx, width):
    """Move the outline dx units sideways and set the advance width."""
    if dx:
        detach_shapes(layer)
        layer.applyTransform(QtGui.QTransform(1, 0, 0, 1, dx, 0))
    layer.advanceWidth = width


def run(glyphs, masters, angle, pivot, mode, lsb_value, rsb_value, do_lsb=True, do_rsb=True):
    """Apply to every editable layer; one Undo step. Returns a summary dict."""
    changed_layers, changed_glyphs, skipped, edits = [], [], [], []
    for glyph in glyphs:
        touched = False
        for master, layer in master_layers(glyph, masters).items():
            if layer.autoLayer:
                skipped.append(f"{glyph.name}/{master} (auto layer)")
                continue
            values = plan(layer, angle, pivot, mode, lsb_value, rsb_value, do_lsb, do_rsb)
            if values is None:
                continue
            dx, new_width = values[4], values[5]
            if dx == 0 and new_width == layer.advanceWidth:
                continue
            edits.append(lambda layer=layer, dx=dx, width=new_width: shift_and_set(layer, dx, width))
            changed_layers.append(layer)
            touched = True
        if touched:
            changed_glyphs.append(glyph)
    # Undo needs the same list notified before and after the edit; auto layers are never in it.
    items = changed_layers + changed_glyphs
    if items:
        fontlab.flItems().notifyChangesApplied(TITLE, items)
        for edit in edits:
            edit()
        fontlab.flItems().notifyChangesApplied(TITLE, items)
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


def make_table(headers):
    table = QtGui.QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
    table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
    header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
    table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    table.setMinimumHeight(220)
    return table


class ItalicSidebearings(QtGui.QDialog):
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
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.font_angle = self.package.italicAngle_value if self.package else 0.0
        x_height = self.package.xHeight_value if self.package else 500
        self.preview = {}
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
        self.angle = QtGui.QDoubleSpinBox()
        self.angle.setRange(-45.0, 45.0)
        self.angle.setDecimals(1)
        self.angle.setSuffix(" °")
        self.angle.setValue(self.font_angle)
        self.angle.setAlignment(QtCore.Qt.AlignRight)
        self.pivot = QtGui.QSpinBox()
        self.pivot.setRange(-2000, 4000)
        self.pivot.setValue(round(x_height / 2))
        self.pivot.setAlignment(QtCore.Qt.AlignRight)
        self.mode = QtGui.QComboBox()
        for label, _ in MODES:
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
        form.addWidget(QtGui.QLabel("Italic angle"), 0, 0)
        form.addWidget(self.angle, 0, 1)
        form.addWidget(QtGui.QLabel("Measured at y ="), 0, 2)
        form.addWidget(self.pivot, 0, 3)
        form.addWidget(QtGui.QLabel("Operation"), 1, 0)
        form.addWidget(self.mode, 1, 1, 1, 3)
        form.addWidget(self.lsb_check, 2, 0)
        form.addWidget(self.lsb, 2, 1)
        form.addWidget(self.rsb_check, 2, 2)
        form.addWidget(self.rsb, 2, 3)
        form.addWidget(QtGui.QLabel("Masters"), 3, 0)
        form.addWidget(self.scope, 3, 1, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        root.addLayout(form)

        self.table = make_table(["Glyph · master", "LSB", "RSB", "Italic LSB", "Italic RSB", "New it. LSB", "New it. RSB"])
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

        for widget in (self.lsb, self.rsb, self.pivot):
            self._connect(widget.valueChanged, lambda *a: self.refresh())
        self._connect(self.angle.valueChanged, lambda *a: self.refresh())
        for widget in (self.lsb_check, self.rsb_check):
            self._connect(widget.toggled, lambda *a: self.refresh())
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _spin(self):
        spin = QtGui.QSpinBox()
        spin.setRange(-2000, 2000)
        spin.setAlignment(QtCore.Qt.AlignRight)
        return spin

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

    def mode_key(self):
        return MODES[self.mode.currentIndex][1]

    def options(self):
        return (self.angle.value, self.pivot.value, self.mode_key(), self.lsb.value, self.rsb.value,
                self.lsb_check.isChecked(), self.rsb_check.isChecked())

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
            upright = " (font is upright: italic values equal plain ones)" if not self.font_angle else ""
            self.subtitle.setText(f"{count} glyph{'s' if count != 1 else ''}: {names} · font angle {self.font_angle:g}°{upright}")
        rows, self.preview = [], {}
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()).items():
                label = f"{glyph.name} · {master}"
                if layer.autoLayer:
                    rows.append((label, "auto layer", "", "", "", "skipped", ""))
                    continue
                values = plan(layer, *self.options())
                if values is None:
                    rows.append((label, "–", "–", "–", "–", "empty", ""))
                    continue
                ilsb, irsb, new_ilsb, new_irsb, _, _ = values
                box = layer.boundingBox
                lsb, rsb = box.x(), layer.advanceWidth - box.x() - box.width()
                self.preview[(glyph.name, master)] = (round(ilsb), round(irsb))
                rows.append((label,) + tuple(str(round(v)) for v in (lsb, rsb, ilsb, irsb, new_ilsb, new_irsb)))
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if column >= 5 and text and text != cells[column - 2]:
                    bold = item.font()
                    bold.setBold(True)
                    item.setFont(bold)
                    item.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, column, item)
        self.apply_button.setEnabled(bool(rows))
        self.status.setText(f"{len(rows)} layer{'s' if len(rows) != 1 else ''} in preview · de-slanted at {self.angle.value:g}°")

    def apply(self):
        result = run(self.glyphs, self.chosen_masters(), *self.options())
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
    dialog = ItalicSidebearings(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
