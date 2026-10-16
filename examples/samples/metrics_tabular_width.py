#FLM: Metrics · Tabular Width
# this_file: samples/metrics_tabular_width.py
"""Give figures (and optionally currency signs) one shared advance width, each outline centred.

Pick a preset glyph set or use the selection, then the width: the widest glyph of the set on
each master, or a fixed value. Tabular figures line up in columns of numbers; this is the
spacing half of that job. One Apply is one Undo step; auto layers are skipped.

Edit > Undo restores outlines, anchors and advances. Stem hints that moved with the outline
keep their new positions after Undo: FontLab does not restore them (measured natively).
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Tabular Width"
KEY = "metrics_tabular_width"
FIGURES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
CURRENCY = ["dollar", "cent", "sterling", "yen", "Euro", "euro", "currency", "franc", "lira", "rupee", "won"]
SETS = [("Figures (zero – nine)", FIGURES), ("Figures and currency", FIGURES + CURRENCY), ("Selected glyphs", None)]
WIDTHS = [("Widest in set, per master", "widest"), ("Fixed width", "fixed")]


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
def extent(layer):
    box = layer.boundingBox
    if box.width() <= 0 and box.height() <= 0:
        return None
    return box.x(), box.x() + box.width()


def target_widths(glyphs, masters, mode, fixed):
    """{master: width}: the set's widest advance per master, or the fixed value everywhere."""
    if mode == "fixed":
        return {master: fixed for master in masters}
    widest = {}
    for glyph in glyphs:
        for master, layer in master_layers(glyph, masters).items():
            widest[master] = max(widest.get(master, 0), round(layer.advanceWidth))
    return widest


def plan(layer, new_width):
    """(width, lsb, new_lsb) with the outline centred in new_width, or None when empty."""
    edges = extent(layer)
    if edges is None:
        return None
    left, right = edges
    white = new_width - round(right - left)
    return round(layer.advanceWidth), round(left), white // 2


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


def run(glyphs, masters, mode, fixed):
    """Set and centre every editable layer; one Undo step. Returns a summary dict."""
    widths = target_widths(glyphs, masters, mode, fixed)
    changed_layers, changed_glyphs, skipped, edits = [], [], [], []
    for glyph in glyphs:
        touched = False
        for master, layer in master_layers(glyph, masters).items():
            if layer.autoLayer:
                skipped.append(f"{glyph.name}/{master} (auto layer)")
                continue
            values = plan(layer, widths[master])
            if values is None:
                continue
            width, lsb, new_lsb = values
            if (width, lsb) == (widths[master], new_lsb):
                continue
            edits.append(lambda layer=layer, dx=new_lsb - lsb, width=widths[master]: shift_and_set(layer, dx, width))
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
    return {"layers": len(changed_layers), "glyphs": len(changed_glyphs), "skipped": skipped, "widths": widths}


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
    table.setMinimumHeight(240)
    return table


class Tabular(QtGui.QDialog):
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
        self.selection = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.glyphs = []
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
        self.glyph_set = QtGui.QComboBox()
        for label, _ in SETS:
            self.glyph_set.addItem(label)
        self.width_mode = QtGui.QComboBox()
        for label, _ in WIDTHS:
            self.width_mode.addItem(label)
        self.fixed = QtGui.QSpinBox()
        self.fixed.setRange(1, 5000)
        self.fixed.setValue(500)
        self.fixed.setAlignment(QtCore.Qt.AlignRight)
        self.fixed.setSuffix(" units")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        form.addWidget(self.glyph_set, 0, 1, 1, 2)
        form.addWidget(QtGui.QLabel("Width"), 1, 0)
        form.addWidget(self.width_mode, 1, 1)
        form.addWidget(self.fixed, 1, 2)
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1, 1, 2)
        form.setColumnStretch(1, 2)
        form.setColumnStretch(2, 1)
        root.addLayout(form)

        self.table = make_table(["Glyph · master", "Width", "LSB", "New width", "New LSB"])
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

        self._connect(self.glyph_set.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.width_mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.fixed.valueChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

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
        return WIDTHS[self.width_mode.currentIndex][1]

    def set_glyphs(self):
        names = SETS[self.glyph_set.currentIndex][1]
        if names is None or self.package is None:
            return list(self.selection)
        glyphs = [self.package.findName(name) for name in names]
        return [g for g in glyphs if g is not None]

    def refresh(self):
        self.refresh_listing()
        show_rebuilds(self, [g.name for g in self.glyphs])

    def refresh_listing(self):
        self.glyphs = self.set_glyphs()
        self.fixed.setEnabled(self.mode_key() == "fixed")
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("None of these glyphs is in the font. Choose another set or select glyphs.")
        else:
            names = " ".join(g.name for g in self.glyphs[:12]) + (" …" if count > 12 else "")
            self.subtitle.setText(f"{count} glyph{'s' if count != 1 else ''} get one width per master: {names}")
        widths = target_widths(self.glyphs, self.chosen_masters(), self.mode_key(), self.fixed.value)
        rows = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()).items():
                label = f"{glyph.name} · {master}"
                if layer.autoLayer:
                    rows.append((label, "auto layer", "", "skipped", ""))
                    continue
                values = plan(layer, widths[master])
                if values is None:
                    rows.append((label, str(round(layer.advanceWidth)), "–", "empty", ""))
                    continue
                width, lsb, new_lsb = values
                rows.append((label, str(width), str(lsb), str(widths[master]), str(new_lsb)))
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if column >= 3 and text and text != cells[column - 2]:
                    bold = item.font()
                    bold.setBold(True)
                    item.setFont(bold)
                    item.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, column, item)
        summary = " · ".join(f"{m} {w}" for m, w in widths.items())
        self.status.setText(f"Target: {summary}" if summary else "Nothing to change")
        self.apply_button.setEnabled(bool(rows))

    def apply(self):
        result = run(self.glyphs, self.chosen_masters(), self.mode_key(), self.fixed.value)
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
    dialog = Tabular(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
