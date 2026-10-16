#FLM: Metrics · Round Advances
# this_file: samples/metrics_round_advances.py
"""Round advance widths to a step (2, 5, 10 … units), keeping every outline where it is.

Only the right sidebearing absorbs the change, so the left sidebearing is preserved. Choose
nearest, up or down, the selected glyphs or the whole font, one or all masters; the table lists
only the layers that change. One Apply is one Undo step; auto layers are skipped.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Round Advances"
KEY = "metrics_round_advances"
DIRECTIONS = [("Nearest", "nearest"), ("Up", "up"), ("Down", "down")]


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


def all_glyphs(package):
    try:
        import FL

        font = FL.fl.font
        names = [font[i].name for i in range(len(font))]
    except Exception:
        names = []
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
def rounded(width, step, direction):
    """width rounded to a multiple of step; halves go up for 'nearest'."""
    if direction == "up":
        return int(math.ceil(width / step) * step)
    if direction == "down":
        return int(math.floor(width / step) * step)
    return int(math.floor(width / step + 0.5) * step)


def changes(glyphs, masters, step, direction):
    """[(glyph, master, layer, width, new_width)] for editable layers whose width changes."""
    out = []
    for glyph in glyphs:
        for master, layer in master_layers(glyph, masters).items():
            if layer.autoLayer:
                continue
            width = layer.advanceWidth
            new = rounded(width, step, direction)
            if new != width:
                out.append((glyph, master, layer, width, new))
    return out


def run(glyphs, masters, step, direction):
    """Round every editable layer's advance; one Undo step. Returns a summary dict."""
    todo = changes(glyphs, masters, step, direction)
    layers, touched = [], []
    for glyph, _, layer, _, new in todo:
        layers.append(layer)
        if glyph not in touched:
            touched.append(glyph)
    # Undo needs the same list notified before and after the edit; auto layers are never in it.
    items = layers + touched
    if items:
        fontlab.flItems().notifyChangesApplied(TITLE, items)
        for _, _, layer, _, new in todo:
            layer.advanceWidth = new
        fontlab.flItems().notifyChangesApplied(TITLE, items)
    autos = sum(1 for g in glyphs for l in master_layers(g, masters).values() if l.autoLayer)
    return {"layers": len(layers), "glyphs": len(touched), "auto_skipped": autos}


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


class RoundAdvances(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(520)
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
        self.step = QtGui.QSpinBox()
        self.step.setRange(2, 100)
        self.step.setValue(10)
        self.step.setAlignment(QtCore.Qt.AlignRight)
        self.step.setSuffix(" units")
        self.direction = QtGui.QComboBox()
        for label, _ in DIRECTIONS:
            self.direction.addItem(label)
        self.which = QtGui.QComboBox()
        self.which.addItem(f"Selected glyphs ({len(self.selection)})")
        self.which.addItem("All glyphs in the font")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Step"), 0, 0)
        form.addWidget(self.step, 0, 1)
        form.addWidget(QtGui.QLabel("Round"), 0, 2)
        form.addWidget(self.direction, 0, 3)
        form.addWidget(QtGui.QLabel("Glyphs"), 1, 0)
        form.addWidget(self.which, 1, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        root.addLayout(form)

        self.table = make_table(["Glyph · master", "Width", "New width", "RSB change"])
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

        for combo in (self.direction, self.which, self.scope):
            self._connect(combo.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.step.valueChanged, lambda *a: self.refresh())
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

    def direction_key(self):
        return DIRECTIONS[self.direction.currentIndex][1]

    def refresh(self):
        self.refresh_listing()
        show_rebuilds(self, [g.name for g in self.glyphs])

    def refresh_listing(self):
        if self.package is None:
            self.glyphs = []
            self.subtitle.setText("Open a font first.")
        else:
            self.glyphs = self.selection if self.which.currentIndex == 0 else all_glyphs(self.package)
            if not self.glyphs:
                self.subtitle.setText("Select glyphs in the Font window, or choose All glyphs.")
            else:
                self.subtitle.setText(f"Rounds the advance of {len(self.glyphs)} glyph{'s' if len(self.glyphs) != 1 else ''}"
                                      f" to multiples of {self.step.value}; outlines and LSB stay put.")
        todo = changes(self.glyphs, self.chosen_masters(), self.step.value, self.direction_key())
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(todo))
        for row, (glyph, master, _, width, new) in enumerate(todo):
            delta = new - width
            cells = [f"{glyph.name} · {master}", f"{width:g}", str(new), f"{delta:+g}"]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if column == 2:
                    bold = item.font()
                    bold.setBold(True)
                    item.setFont(bold)
                    item.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, column, item)
        self.status.setText(f"{len(todo)} layer{'s' if len(todo) != 1 else ''} will change" if todo else "All advances are already rounded")
        self.apply_button.setEnabled(bool(todo))

    def apply(self):
        result = run(self.glyphs, self.chosen_masters(), self.step.value, self.direction_key())
        self.last_result = result
        fontlab.UpdateAll()
        self.refresh()
        note = f" · {result['auto_skipped']} auto layers skipped" if result["auto_skipped"] else ""
        self.status.setText(f"Rounded {result['layers']} advances in {result['glyphs']} glyphs{note}")

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
    dialog = RoundAdvances(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
