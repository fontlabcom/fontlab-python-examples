#FLM: Outlines · Node Statistics
# this_file: samples/outlines_node_statistics.py
"""Contours and nodes per glyph and master in one table, with incompatible glyphs flagged.

Each cell reads "contours / nodes" for a master; a glyph is flagged when its masters differ,
which breaks interpolation. Work on the selection or the whole font, then select the flagged
glyphs in the Font window with one click. Read-only: nothing in the font changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Node Statistics"
KEY = "outlines_node_statistics"


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


# ---------------------------------------------------------------- core
def layer_counts(layer):
    """(contours, nodes) drawn in the layer, or None for an auto layer."""
    if layer.autoLayer:
        return None
    contours = own_contours(layer)
    return len(contours), sum(contour.nodesCount for contour in contours)


def glyph_counts(glyph, masters):
    return {master: layer_counts(layer) for master, layer in master_layers(glyph, masters).items()}


def incompatible(counts):
    values = {value for value in counts.values() if value is not None}
    return len(values) > 1


def all_names(package):
    import FL

    font = FL.fl.font
    return [font[i].name for i in range(len(font))]


def select_in_font_window(names):
    import FL

    font = FL.fl.font
    wanted = set(names)
    for i in range(len(font)):
        FL.fl.Select(i, 1 if font[i].name in wanted else 0)


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


class NodeStatistics(SampleDialog):
    ACTION = "Select Flagged"

    def build(self):
        grid = self.form()
        self.source = QtGui.QComboBox()
        self.source.addItem(f"Selected glyphs ({len(self.names)})")
        self.source.addItem("Whole font")
        self._connect(self.source.currentIndexChanged, lambda *a: self.refresh())
        self.only_flagged = QtGui.QCheckBox("Show flagged glyphs only")
        self._connect(self.only_flagged.toggled, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        grid.addWidget(self.source, 0, 1)
        grid.addWidget(self.only_flagged, 0, 2)
        grid.setColumnStretch(1, 1)
        self.table = make_table(["Glyph"] + list(self.masters) + ["Masters"], 300)
        self.root.addWidget(self.table, 1)

    def source_names(self):
        if self.package is None:
            return []
        return all_names(self.package) if self.source.currentIndex == 1 else self.names

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.apply_button.setEnabled(False)
            return
        names = self.source_names()
        self.data, self.flagged = {}, []
        for name in names:
            glyph = self.package.findName(name)
            if glyph is not None:
                self.data[name] = glyph_counts(glyph, self.masters)
                if incompatible(self.data[name]):
                    self.flagged.append(name)
        self.subtitle.setText(f"{len(self.data)} glyphs × {len(self.masters)} masters · "
                              f"cells show contours / nodes drawn in each master")
        rows, odd = [], {}
        for name, counts in self.data.items():
            if self.only_flagged.isChecked() and name not in self.flagged:
                continue
            values = [v for v in counts.values() if v is not None]
            common = max(set(values), key=values.count) if values else None
            cells = [name]
            for column, master in enumerate(self.masters, start=1):
                value = counts.get(master)
                cells.append("auto" if value is None else f"{value[0]} / {value[1]}")
                if value is not None and value != common:
                    odd[(len(rows), column)] = True
            cells.append("✗ differ" if name in self.flagged else "✓")
            rows.append(tuple(cells))
        last = len(self.masters) + 1
        fill_table(self.table, rows, lambda r, c, text: odd.get((r, c), False) or c == last and text.startswith("✗"))
        self.apply_button.setEnabled(bool(self.flagged))
        self.status.setText(f"{len(self.flagged)} of {len(self.data)} glyphs have masters that differ")

    def apply(self):
        select_in_font_window(self.flagged)
        self.last_result = {"selected": list(self.flagged)}
        fontlab.UpdateAll()
        self.status.setText(f"Selected {len(self.flagged)} flagged glyphs in the Font window")


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = NodeStatistics(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
