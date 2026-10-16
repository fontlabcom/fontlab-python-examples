#FLM: Outlines · Round Coordinates
# this_file: samples/outlines_round_coordinates.py
"""Round node coordinates of the selected glyphs to a grid, optionally anchors and component offsets.

Fractional or off-grid coordinates come from scaling, interpolation and imports. A table
previews how many nodes, anchors and component offsets are off the grid per glyph and master;
Apply snaps them (halves away from zero) as one Undo step. Auto layers are skipped.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Round Coordinates"
KEY = "outlines_round_coordinates"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def selected_names():
    """Glyph names selected in the Font window, in font order; else the current glyph."""
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
    return names


def master_layers(glyph, masters):
    """{master: flLayer} for the masters present in this glyph."""
    found = {}
    for master in masters:
        layer = glyph.findLayer(master)
        if layer is not None and not layer.isNull:
            found[master] = layer
    return found


def own_contours(layer):
    """Contours drawn in this layer; layer.getContours() also lists the contours of components."""
    return [contour for shape in layer.shapes if not shape.isComponent for contour in shape.contours]


def swap_for_clones(layer):
    """FontLab's history keeps references to shapes, so in-place edits leak into the Undo state:
    replace every shape by its clone at the same index and edit the clones."""
    for index, shape in enumerate(list(layer.shapes)):
        clone = shape.clone()
        layer.removeShape(shape)
        layer.insertShape(index, clone)


def undoable(layers, glyphs, edit):
    """One Undo step: notify, swap shapes for clones, run edit(), notify again with the same list."""
    items = list(layers) + list(glyphs)
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    for layer in layers:
        swap_for_clones(layer)
    result = edit()
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    fontlab.UpdateAll()
    return result


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


# ---------------------------------------------------------------- core
def snap(value, grid):
    """Nearest multiple of grid; halves round away from zero."""
    steps = math.floor(abs(value) / grid + 0.5)
    return math.copysign(steps * grid, value) if steps else 0.0


def off_grid(value, grid):
    return abs(snap(value, grid) - value) > 1e-6


def component_shapes(layer):
    return [shape for shape in layer.shapes if shape.isComponent]


def count_layer(layer, grid, do_anchors, do_components):
    """(nodes, anchors, components) off the grid in this layer."""
    nodes = sum(1 for contour in own_contours(layer) for node in contour.nodes()
                if off_grid(node.x, grid) or off_grid(node.y, grid))
    anchors = sum(1 for a in layer.anchors if off_grid(a.point.x(), grid) or off_grid(a.point.y(), grid)) if do_anchors else 0
    components = sum(1 for s in component_shapes(layer) if off_grid(s.transform.dx(), grid) or off_grid(s.transform.dy(), grid)
                     ) if do_components else 0
    return nodes, anchors, components


def round_layer(layer, grid, do_anchors, do_components):
    changed = 0
    for contour in own_contours(layer):
        for node in contour.nodes():
            x, y = snap(node.x, grid), snap(node.y, grid)
            if (x, y) != (node.x, node.y):
                node.x, node.y = x, y
                changed += 1
    if do_anchors:
        for anchor in layer.anchors:
            p = anchor.point
            x, y = snap(p.x(), grid), snap(p.y(), grid)
            if (x, y) != (p.x(), p.y()):
                anchor.point = QtCore.QPointF(x, y)
                changed += 1
    if do_components:
        for shape in component_shapes(layer):
            t = shape.transform
            dx, dy = snap(t.dx(), grid), snap(t.dy(), grid)
            if (dx, dy) != (t.dx(), t.dy()):
                shape.transform = QtGui.QTransform(t.m11(), t.m12(), t.m21(), t.m22(), dx, dy)
                changed += 1
    return changed


# ---------------------------------------------------------------- GUI kit
def muted(widget, alpha=150):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
    color.setAlpha(alpha)
    return color.name(QtGui.QColor.HexArgb)


def make_table(headers, min_height=280):
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
    table.setMinimumHeight(min_height)
    return table


def compact(spin, width=150):
    """Spin boxes read better at a fixed width than stretched across the form."""
    spin.setAlignment(QtCore.Qt.AlignRight)
    spin.setMaximumWidth(width)
    return readable(spin)


def readable(spin):
    """Spin box values render pale in FontLab's inactive palette: pin the text to WindowText."""
    spin.setStyleSheet(f"color: {spin.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText).name()};")
    return spin


def fill_table(table, rows, highlight=None):
    """Fill a QTableWidget; a 2-tuple row (label, note) shows the note muted across the row."""
    accent = QtGui.QColor(table.palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link))  # copy: color() can alias the palette
    ink = QtGui.QColor(table.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
    note_color = QtGui.QColor(ink)
    note_color.setAlpha(130)
    table.clearSpans()
    table.setRowCount(0)
    table.setRowCount(len(rows))
    for row, cells in enumerate(rows):
        for column, text in enumerate(cells):
            item = QtGui.QTableWidgetItem(text)
            item.setForeground(QtGui.QBrush(ink))
            if len(cells) == 2 and column == 1:
                item.setForeground(QtGui.QBrush(note_color))
                if table.columnCount > 2:
                    table.setSpan(row, 1, 1, table.columnCount - 1)
            elif column:
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if highlight is not None and highlight(row, column, text):
                    bold = item.font()
                    bold.setBold(True)
                    item.setFont(bold)
                    item.setForeground(QtGui.QBrush(accent))
            table.setItem(row, column, item)


class SampleDialog(QtGui.QDialog):
    """Heading, muted subtitle, the subclass's body, then a footer: status, Close, action button."""

    ACTION = "Apply"

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(520)
        # FontLab can report a light Text colour on a light Base, and its inactive group is paler
        # still (a dialog loses focus to the Font window after Apply): use the active WindowText.
        palette = self.palette
        ink = QtGui.QColor(palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
        for group in (QtGui.QPalette.Active, QtGui.QPalette.Inactive):
            for role in (QtGui.QPalette.WindowText, QtGui.QPalette.Text, QtGui.QPalette.ButtonText):
                palette.setColor(group, role, ink)
            palette.setColor(group, QtGui.QPalette.Link, palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link))
        self.setPalette(palette)
        self.package = current_package()
        self.names = selected_names() if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self._connections = []
        self.last_error = ""

        self.root = QtGui.QVBoxLayout(self)
        self.root.setContentsMargins(20, 18, 20, 16)
        self.root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        self.root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        self.root.addWidget(self.subtitle)

        self.build()

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.close_button)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        if self.ACTION:
            self.apply_button = QtGui.QPushButton(self.ACTION)
            self.apply_button.setDefault(True)
            footer.addWidget(self.apply_button)
            self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self.root.addLayout(footer)
        try:
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def _connect(self, signal, slot):
        """Connect through a guard: an exception in a slot is shown in the status line, never raised into Qt."""
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:
                self.show_error(error)
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def paint_report(self, text):
        """Painters call this when drawing failed; the message stays in last_error for tests."""
        self.last_error = text
        self.status.setText(text)

    def show_error(self, error):
        self.last_error = f"{type(error).__name__}: {error}"
        status = getattr(self, "status", None)
        if status is not None:
            status.setText(f"Error: {self.last_error}")

    def scope_combo(self):
        combo = QtGui.QComboBox()
        combo.addItem(f"Current master ({self.current_master})")
        combo.addItem(f"All masters ({len(self.masters)})")
        self._connect(combo.currentIndexChanged, lambda *a: self.refresh())
        return combo

    def chosen_masters(self):
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def form(self):
        grid = QtGui.QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        self.root.addLayout(grid)
        return grid

    def describe_selection(self, what="glyph"):
        """Subtitle for the selection; False when there is nothing to work on."""
        count = len(self.names)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return False
        if not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
            return False
        shown = ", ".join(self.names[:8]) + (" …" if count > 8 else "")
        self.subtitle.setText(f"{count} {what}{'s' if count != 1 else ''}: {shown}")
        return True

    def glyphs(self):
        found = [self.package.findName(name) for name in self.names] if self.package else []
        return [glyph for glyph in found if glyph is not None]

    def build(self):
        pass

    def refresh(self):
        pass

    def apply(self):
        pass

    def closeEvent(self, event):
        self.teardown()
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        getattr(sys, "_fontlab_samples", {}).pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)

    def teardown(self):
        pass


class LayerEditDialog(SampleDialog):
    """Preview table of glyph · master rows, then one Undo step editing every listed layer.

    Subclasses set HEADERS and implement preview(name, master, layer) -> (cells, pending)
    and edit(name, master, layer) -> number of changes. Auto layers are listed and skipped.
    """

    HEADERS = ["Glyph · master"]
    UNIT = "change"

    def build_table(self):
        self.table = make_table(self.HEADERS)
        self.root.addWidget(self.table, 1)

    def highlight(self, row, column, text):
        return False

    def layers(self):
        for glyph in self.glyphs():
            for master, layer in master_layers(glyph, self.chosen_masters()).items():
                yield glyph, master, layer

    def refresh(self):
        if not self.describe_selection():
            fill_table(self.table, [])
            self.apply_button.setEnabled(False)
            self.status.setText("")
            return
        rows, pending, editing = [], 0, []
        for glyph, master, layer in self.layers():
            label = f"{glyph.name} · {master}"
            if layer.autoLayer:
                rows.append((label, "auto layer · skipped"))
                continue
            cells, count = self.preview(glyph.name, master, layer)
            pending += count
            if count and glyph.name not in editing:
                editing.append(glyph.name)
            rows.append((label,) + tuple(cells))
        self.rows = rows
        fill_table(self.table, rows, self.highlight)
        self.apply_button.setEnabled(pending > 0)
        self.status.setText(f"{pending} {self.UNIT}{'s' if pending != 1 else ''} pending")
        show_rebuilds(self, editing)

    def prepare(self):
        """Hook: plan the edits once the shapes are clones (earlier contour references are stale)."""

    def apply(self):
        targets, skipped = [], []
        for glyph, master, layer in list(self.layers()):
            if layer.autoLayer:
                skipped.append(f"{glyph.name}/{master}")
            elif self.preview(glyph.name, master, layer)[1]:
                targets.append((glyph, master, layer))
        layers = [layer for _, _, layer in targets]
        glyphs = []
        for glyph, _, _ in targets:
            if glyph not in glyphs:
                glyphs.append(glyph)

        def edit_all():
            self.prepare()
            return sum(self.edit(glyph.name, master, layer) for glyph, master, layer in targets)

        total = undoable(layers, glyphs, edit_all) if targets else 0
        self.last_result = {"changes": total, "layers": len(layers), "glyphs": len(glyphs), "skipped": skipped}
        self.refresh()
        note = f" · {len(skipped)} auto layers skipped" if skipped else ""
        self.status.setText(f"{total} {self.UNIT}{'s' if total != 1 else ''} in {len(glyphs)} glyphs{note}")


class Rounder(LayerEditDialog):
    HEADERS = ["Glyph · master", "Nodes", "Anchors", "Components"]
    UNIT = "value"

    def build(self):
        grid = self.form()
        self.grid = compact(QtGui.QSpinBox(), 130)
        self.grid.setRange(1, 100)
        self.grid.setValue(1)
        self.grid.setSuffix(" units")
        self._connect(self.grid.valueChanged, lambda *a: self.refresh())
        self.anchors_check = QtGui.QCheckBox("Anchors")
        self.anchors_check.setChecked(True)
        self.components_check = QtGui.QCheckBox("Component offsets")
        self.components_check.setChecked(True)
        for box in (self.anchors_check, self.components_check):
            self._connect(box.toggled, lambda *a: self.refresh())
        self.scope = self.scope_combo()
        grid.addWidget(QtGui.QLabel("Grid"), 0, 0)
        grid.addWidget(self.grid, 0, 1)
        grid.addWidget(self.anchors_check, 0, 2)
        grid.addWidget(self.components_check, 0, 3)
        grid.addWidget(QtGui.QLabel("Masters"), 1, 0)
        grid.addWidget(self.scope, 1, 1, 1, 4)
        grid.setColumnStretch(4, 1)
        self.build_table()

    def highlight(self, row, column, text):
        return text.isdigit() and text != "0"

    def options(self):
        return self.grid.value, self.anchors_check.isChecked(), self.components_check.isChecked()

    def preview(self, name, master, layer):
        counts = count_layer(layer, *self.options())
        return tuple(str(c) for c in counts), sum(counts)

    def edit(self, name, master, layer):
        return round_layer(layer, *self.options())


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = Rounder(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
