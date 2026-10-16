#FLM: Outlines · Add Extremes
# this_file: samples/outlines_add_extremes.py
"""Insert on-curve nodes at the horizontal and vertical extremes of curve segments.

Extremes are solved from each cubic's derivative; points within a small margin of an existing
node are ignored. FontLab's own split (``flContour.insertNodeTo``) inserts the nodes, so the
curve shape is kept. The table shows node counts before and after per glyph and master;
"Only when every master gets the same nodes" keeps masters compatible.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Add Extremes"
KEY = "outlines_add_extremes"
MARGIN = 0.02  # ignore extremes this close (in t) to a segment end


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


def node_points(contour):
    return [(node.x, node.y, bool(node.isOn())) for node in contour.nodes()]


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
def segments(points):
    """[(index, (p0, p1, p2, p3))] cubic segments of a closed contour starting at node 0."""
    result, start, handles, k = [], points[0][:2], [], 0
    for x, y, on in points[1:] + points[:1]:
        if not on:
            handles.append((x, y))
            continue
        if len(handles) == 2:
            result.append((k, (start, handles[0], handles[1], (x, y))))
        k += 1
        start, handles = (x, y), []
    return result


def roots(a, b, c):
    """Real roots of a t^2 + b t + c within (MARGIN, 1 - MARGIN)."""
    if abs(a) < 1e-9:
        found = [-c / b] if abs(b) > 1e-9 else []
    else:
        disc = b * b - 4 * a * c
        if disc < 0:
            return []
        q = math.sqrt(disc)
        found = [(-b + q) / (2 * a), (-b - q) / (2 * a)]
    return sorted({round(t, 6) for t in found if MARGIN < t < 1 - MARGIN})


def extremes(p0, p1, p2, p3):
    """Parameters t of x and y extremes of one cubic."""
    ts = set()
    for axis in (0, 1):
        a = -p0[axis] + 3 * p1[axis] - 3 * p2[axis] + p3[axis]
        b = 2 * (p0[axis] - 2 * p1[axis] + p2[axis])
        c = p1[axis] - p0[axis]
        ts.update(roots(a, b, c))
    return sorted(ts)


def contour_plan(contour):
    """[(segment index, [t, ...])] for one contour, first node on-curve assumed."""
    points = node_points(contour)
    if not points or not points[0][2]:
        return []
    return [(k, ts) for k, seg in segments(points) for ts in [extremes(*seg)] if ts]


def layer_plan(layer):
    return [(contour, plan) for contour in own_contours(layer) for plan in [contour_plan(contour)] if plan]


def insert_extremes(contour, plan):
    """Insert from the last segment back so earlier segment indices stay valid."""
    added = 0
    for k, ts in sorted(plan, reverse=True):
        upper = 1.0
        for t in sorted(ts, reverse=True):
            contour.insertNodeTo(k + t / upper)  # the segment now ends at the previous split
            upper = t
            added += 1
    return added


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


class Extremes(LayerEditDialog):
    HEADERS = ["Glyph · master", "Nodes", "Extremes to add", "Nodes after"]
    UNIT = "node"

    def build(self):
        grid = self.form()
        self.scope = self.scope_combo()
        self.compatible = QtGui.QCheckBox("Only when every master gets the same nodes")
        self.compatible.setChecked(True)
        self._connect(self.compatible.toggled, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Masters"), 0, 0)
        grid.addWidget(self.scope, 0, 1)
        grid.addWidget(self.compatible, 1, 1)
        grid.setColumnStretch(1, 1)
        self.build_table()

    def counts(self, layer):
        return [sum(len(ts) for _, ts in plan) for _, plan in layer_plan(layer)]

    def blocked(self, name):
        """True when masters would get different extremes (compatibility guard)."""
        if not self.compatible.isChecked():
            return False
        glyph = self.package.findName(name)
        signatures = {tuple(self.counts(layer)) for layer in master_layers(glyph, self.chosen_masters()).values()
                      if not layer.autoLayer}
        return len(signatures) > 1

    def highlight(self, row, column, text):
        return column == 2 and text not in ("0", "")

    def preview(self, name, master, layer):
        nodes = sum(c.nodesCount for c in own_contours(layer))
        add = sum(self.counts(layer))
        if add and self.blocked(name):
            return (str(nodes), "masters differ · skipped", str(nodes)), 0
        return (str(nodes), str(add), str(nodes + 3 * add)), add

    def edit(self, name, master, layer):
        return sum(insert_extremes(contour, plan) for contour, plan in layer_plan(layer))


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = Extremes(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
