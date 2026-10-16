#FLM: Outlines · Delete Small Contours
# this_file: samples/outlines_delete_small_contours.py
"""Remove contours whose area is below a threshold: stray specks left by drawing or tracing.

Area is measured on the flattened outline (square units). The table lists every contour under
the threshold with its area and position before anything is deleted; uncheck "Delete" by raising
or lowering the threshold. One Apply is one Undo step; auto layers are skipped.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Delete Small Contours"
KEY = "outlines_delete_small_contours"
STEPS = 12


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
def polygon(points):
    """Flatten [(x, y, on)] of a closed contour: cubic for two handles, polyline otherwise."""
    if not points:
        return []
    start = next((i for i, p in enumerate(points) if p[2]), 0)
    pts = points[start:] + points[:start]
    poly, handles, current = [pts[0][:2]], [], pts[0][:2]
    for x, y, on in pts[1:] + pts[:1]:
        if not on:
            handles.append((x, y))
            continue
        if len(handles) == 2:
            (ax, ay), (bx, by), (cx, cy), (dx, dy) = current, handles[0], handles[1], (x, y)
            for i in range(1, STEPS + 1):
                t = i / STEPS
                u = 1 - t
                poly.append((u ** 3 * ax + 3 * u * u * t * bx + 3 * u * t * t * cx + t ** 3 * dx,
                             u ** 3 * ay + 3 * u * u * t * by + 3 * u * t * t * cy + t ** 3 * dy))
        else:
            poly.extend(handles)
            poly.append((x, y))
        current, handles = (x, y), []
    poly.extend(handles)
    return poly


def area(points):
    poly = polygon(points)
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))) / 2.0


def small_contours(layer, threshold):
    """[(shape, contour, index, area, (x, y))] for own contours with area < threshold."""
    found, index = [], 0
    for shape in layer.shapes:
        if shape.isComponent:
            continue
        for contour in shape.contours:
            points = node_points(contour)
            value = area(points)
            if value < threshold:
                xs, ys = [p[0] for p in points], [p[1] for p in points]
                found.append((shape, contour, index, value, (min(xs), min(ys))))
            index += 1
    return found


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


class SmallContours(LayerEditDialog):
    HEADERS = ["Glyph · master", "Contour", "Area", "At (x, y)"]
    UNIT = "contour"
    ACTION = "Delete"

    def build(self):
        grid = self.form()
        self.scope = self.scope_combo()
        self.threshold = QtGui.QSpinBox()
        self.threshold.setRange(1, 1000000)
        self.threshold.setSingleStep(100)
        self.threshold.setValue(400)
        self.threshold.setSuffix(" units²")
        compact(self.threshold)
        self._connect(self.threshold.valueChanged, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Smaller than"), 0, 0)
        grid.addWidget(self.threshold, 0, 1)
        grid.addWidget(QtGui.QLabel("Masters"), 1, 0)
        grid.addWidget(self.scope, 1, 1, 1, 2)
        grid.setColumnStretch(2, 1)  # a compact spin box keeps column 1 narrow
        self.build_table()

    def refresh(self):
        LayerEditDialog.refresh(self)
        # One row per small contour reads better than one per layer: expand the preview rows.
        if not getattr(self, "rows", None):
            return
        rows = []
        for glyph, master, layer in self.layers():
            label = f"{glyph.name} · {master}"
            if layer.autoLayer:
                rows.append((label, "auto layer · skipped"))
                continue
            found = small_contours(layer, self.threshold.value)
            if not found:
                rows.append((label, "nothing below the threshold"))
            for _, _, index, value, (x, y) in found:
                rows.append((label, f"#{index + 1}", f"{value:.0f}", f"{x:.0f}, {y:.0f}"))
        self.rows = rows
        fill_table(self.table, rows, lambda r, c, text: c == 2)

    def preview(self, name, master, layer):
        found = small_contours(layer, self.threshold.value)
        return ("", "", ""), len(found)

    def edit(self, name, master, layer):
        found = small_contours(layer, self.threshold.value)
        for shape, contour, _, _, _ in found:
            shape.removeContour(contour)
        return len(found)


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = SmallContours(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
