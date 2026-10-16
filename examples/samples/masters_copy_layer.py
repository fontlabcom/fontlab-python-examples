#FLM: Masters · Copy Layer Between Masters
# this_file: samples/masters_copy_layer.py
"""Copy the outline (and optionally anchors and advance width) from one master to others.

Pick the source master, tick the target masters, preview what each target layer holds now and
what it will get. The targets' own contours are replaced by copies of the source contours;
components stay. Same-named anchors move to the source positions. One Apply is one Undo step.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Copy Layer Between Masters"
KEY = "masters_copy_layer"


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
def replace_outline(source, target):
    """Make target's own contours clones of source's (placed by source shape transforms)."""
    holders = [shape for shape in target.shapes if not shape.isComponent]
    for shape in holders:
        for contour in list(shape.contours):
            shape.removeContour(contour)
    holder = holders[0] if holders else None
    if holder is None:
        holder = fontlab.flShape()
        target.addShape(holder)
    copied = 0
    for shape in source.shapes:
        if shape.isComponent:
            continue
        transform = shape.transform
        for contour in shape.contours:
            clone = contour.clone()
            if not transform.isIdentity():
                for node in clone.nodes():
                    point = transform.map(QtCore.QPointF(node.x, node.y))
                    node.x, node.y = point.x(), point.y()
            holder.addContour(clone, True)
            copied += 1
    return copied


def copy_anchors(source, target):
    """Move target anchors to the positions of same-named source anchors; returns (moved, missing)."""
    moved, missing = 0, []
    for anchor in source.anchors:
        other = target.findAnchor(anchor.name)
        if other is None:
            missing.append(anchor.name)
            continue
        if other.point != anchor.point:
            other.point = QtCore.QPointF(anchor.point.x(), anchor.point.y())
            moved += 1
    return moved, missing


def copy_layer(source, target, anchors=True, width=True):
    copied = replace_outline(source, target)
    moved, missing = copy_anchors(source, target) if anchors else (0, [])
    if width:
        target.advanceWidth = source.advanceWidth
    return {"contours": copied, "anchors": moved, "missing": missing}


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


class CopyLayer(SampleDialog):
    ACTION = "Copy"

    def build(self):
        grid = self.form()
        self.source = QtGui.QComboBox()
        for master in self.masters:
            self.source.addItem(master)
        if self.current_master in self.masters:
            self.source.setCurrentIndex(self.masters.index(self.current_master))
        self._connect(self.source.currentIndexChanged, lambda *a: self.source_changed())
        self.targets = QtGui.QListWidget()
        self.targets.setMaximumHeight(24 * max(2, min(len(self.masters), 5)))
        self._connect(self.targets.itemChanged, lambda *a: self.refresh())
        self.anchors = QtGui.QCheckBox("Anchors")
        self.anchors.setChecked(True)
        self.copy_width = QtGui.QCheckBox("Advance width")
        self.copy_width.setChecked(True)
        for box in (self.anchors, self.copy_width):
            self._connect(box.toggled, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("From"), 0, 0)
        grid.addWidget(self.source, 0, 1, 1, 2)
        grid.addWidget(QtGui.QLabel("To"), 1, 0, int(QtCore.Qt.AlignTop))
        grid.addWidget(self.targets, 1, 1, 1, 2)
        grid.addWidget(QtGui.QLabel("Also"), 2, 0)
        grid.addWidget(self.anchors, 2, 1)
        grid.addWidget(self.copy_width, 2, 2)
        grid.setColumnStretch(2, 1)
        self.table = make_table(["Glyph · target", "Contours now", "Contours after", "Width now", "Width after"])
        self.root.addWidget(self.table, 1)
        self.fill_targets()

    def fill_targets(self):
        self.targets.blockSignals(True)
        self.targets.clear()
        source = self.source.currentText
        for master in self.masters:
            if master == source:
                continue
            item = QtGui.QListWidgetItem(master, self.targets)
            item.setForeground(QtGui.QBrush(self.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText)))
            item.setFlags(int(item.flags() | QtCore.Qt.ItemIsUserCheckable))
            item.setCheckState(QtCore.Qt.Checked)
        self.targets.blockSignals(False)

    def source_changed(self):
        self.fill_targets()
        self.refresh()

    def chosen_targets(self):
        return [self.targets.item(i).text() for i in range(self.targets.count)
                if self.targets.item(i).checkState() == QtCore.Qt.Checked]

    def pairs(self):
        source = self.source.currentText
        for glyph in self.glyphs():
            layers = master_layers(glyph, self.masters)
            if source not in layers:
                continue
            for master in self.chosen_targets():
                if master in layers:
                    yield glyph, layers[source], master, layers[master]

    def refresh(self):
        if not hasattr(self, "table"):
            return
        if not self.describe_selection():
            fill_table(self.table, [])
            self.apply_button.setEnabled(False)
            return
        rows, pending = [], 0
        for glyph, source, master, target in self.pairs():
            label = f"{glyph.name} · {master}"
            if target.autoLayer or source.autoLayer:
                rows.append((label, "auto layer · skipped"))
                continue
            width_after = source.advanceWidth if self.copy_width.isChecked() else target.advanceWidth
            rows.append((label, str(len(own_contours(target))), str(len(own_contours(source))),
                         f"{target.advanceWidth:g}", f"{width_after:g}"))
            pending += 1
        fill_table(self.table, rows, lambda r, c, text: c in (2, 4) and text != rows[r][c - 1])
        self.apply_button.setEnabled(pending > 0)
        self.status.setText(f"{pending} layer{'s' if pending != 1 else ''} will be replaced from {self.source.currentText}")
        show_rebuilds(self, self.names)

    def apply(self):
        pairs, skipped = [], []
        for glyph, source, master, target in list(self.pairs()):
            if target.autoLayer or source.autoLayer:
                skipped.append(f"{glyph.name}/{master}")
            else:
                pairs.append((glyph, source, target))
        targets = [target for _, _, target in pairs]
        glyphs = []
        for glyph, _, _ in pairs:
            if glyph not in glyphs:
                glyphs.append(glyph)
        missing = set()

        def copy_all():
            for _, source, target in pairs:
                missing.update(copy_layer(source, target, self.anchors.isChecked(), self.copy_width.isChecked())["missing"])

        if pairs:
            undoable(targets, glyphs, copy_all)
        self.last_result = {"layers": len(targets), "glyphs": len(glyphs), "skipped": skipped, "missing": sorted(missing)}
        self.refresh()
        note = f" · anchors missing in targets: {', '.join(sorted(missing))}" if missing else ""
        self.status.setText(f"Replaced {len(targets)} layers in {len(glyphs)} glyphs{note}")


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = CopyLayer(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
