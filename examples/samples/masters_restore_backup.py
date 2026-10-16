#FLM: Masters · Restore Backup Layer
# this_file: samples/masters_restore_backup.py
"""Restore a backup layer (such as "Regular backup") into the master it was taken from.

Choose a backup name found in the selected glyphs; its master is the longest master name the
backup name starts with. The master's own contours, same-named anchors and advance width are
replaced by the backup's. Optionally the backup layer is deleted afterwards. One Undo step.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Restore Backup Layer"
KEY = "masters_restore_backup"


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


def master_of(name, masters):
    """The master a backup layer belongs to: the longest master name it starts with."""
    found = [m for m in masters if name == m or name.startswith(m + " ")]
    return max(found, key=len) if found else None


def backup_layers(glyph, masters):
    """{backup name: (layer, master)} for non-master, non-mask layers named after a master."""
    found = {}
    for layer in glyph.layers:
        if layer.isMasterLayer or layer.isMaskLayer:
            continue
        master = master_of(layer.name, masters)
        if master is not None:
            found[layer.name] = (layer, master)
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


class Restore(SampleDialog):
    ACTION = "Restore"

    def build(self):
        grid = self.form()
        self.backup = QtGui.QComboBox()
        self._connect(self.backup.currentIndexChanged, lambda *a: self.refresh())
        self.delete_after = QtGui.QCheckBox("Delete the backup layer after restoring")
        grid.addWidget(QtGui.QLabel("Backup"), 0, 0)
        grid.addWidget(self.backup, 0, 1)
        grid.addWidget(self.delete_after, 1, 1)
        grid.setColumnStretch(1, 1)
        self.table = make_table(["Glyph", "Into master", "Contours", "Width"])
        self.root.addWidget(self.table, 1)
        self.fill_backups()

    def fill_backups(self):
        names = []
        for glyph in self.glyphs():
            for name in backup_layers(glyph, self.masters):
                if name not in names:
                    names.append(name)
        self.backup.blockSignals(True)
        self.backup.clear()
        for name in sorted(names):
            self.backup.addItem(name)
        self.backup.blockSignals(False)

    def pairs(self):
        chosen = self.backup.currentText
        for glyph in self.glyphs():
            found = backup_layers(glyph, self.masters).get(chosen)
            if found is None:
                continue
            layer, master = found
            target = glyph.findLayer(master)
            if target is not None:
                yield glyph, layer, master, target

    def refresh(self):
        if not hasattr(self, "table"):
            return
        if not self.describe_selection():
            fill_table(self.table, [])
            self.apply_button.setEnabled(False)
            return
        if self.backup.count == 0:
            self.fill_backups()
        rows = []
        for glyph, layer, master, target in self.pairs():
            if target.autoLayer:
                rows.append((glyph.name, "auto layer · skipped"))
                continue
            rows.append((glyph.name, master, f"{len(own_contours(layer))} → {len(own_contours(target))}",
                         f"{layer.advanceWidth:g} → {target.advanceWidth:g}"))
        fill_table(self.table, rows, lambda r, c, text: c == 1)
        pending = sum(1 for r in rows if len(r) > 2)
        self.apply_button.setEnabled(pending > 0)
        if self.backup.count == 0:
            self.status.setText("No backup layers in these glyphs. Make some with Back Up Master Layers.")
        else:
            self.status.setText(f"{pending} glyph{'s' if pending != 1 else ''} will get “{self.backup.currentText}” back · cells read backup → master")
            show_rebuilds(self, self.names)

    def apply(self):
        pairs = [(g, layer, target) for g, layer, _, target in list(self.pairs()) if not target.autoLayer]
        targets = [target for _, _, target in pairs]
        glyphs = [glyph for glyph, _, _ in pairs]
        delete = self.delete_after.isChecked()

        def restore():
            for glyph, layer, target in pairs:
                copy_layer(layer, target)
                if delete:
                    glyph.removeLayer(layer)

        if pairs:
            undoable(targets, glyphs, restore)
        deleted = len(pairs) if delete else 0
        self.last_result = {"restored": [g.name for g in glyphs], "deleted": deleted}
        self.fill_backups()
        self.refresh()
        note = f" · deleted {deleted} backup layers" if deleted else ""
        self.status.setText(f"Restored {len(targets)} master layers{note}")


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = Restore(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
