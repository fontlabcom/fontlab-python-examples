#FLM: Masters · Masters Overview
# this_file: samples/masters_overview.py
"""One table of all masters: axis location, vertical metrics and italic angle.

Rows follow the font's master order; the current master is bold. Vertical metrics come from
``fontlab.FontMetrics(package, master)``; FontLab has no per-master italic-angle accessor, so each
master is made current for the read and the original master is restored. Double-click a row to
make that master current. Read-only otherwise.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Masters Overview"
KEY = "masters_overview"
METRICS = [("Ascender", "ascender"), ("Cap height", "capsHeight"), ("x-height", "xHeight"), ("Descender", "descender")]


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


# ---------------------------------------------------------------- core
def location_text(package, master):
    location = package.location(master)
    parts = []
    for axis in package.axes:
        try:
            parts.append(f"{axis.tag} {location[axis.shortName]:g}")
        except Exception:
            parts.append(f"{axis.tag} ?")
    return ", ".join(parts) or "–"


def italic_angles(package, masters):
    """{master: italic angle}; switches the current master briefly and always restores it."""
    current, angles = package.master, {}
    try:
        for master in masters:
            if package.master != master:
                package.setMaster(master)
            angles[master] = float(package.italicAngle_value)
    finally:
        if package.master != current:
            package.setMaster(current)
    return angles


def overview(package):
    """[(master, location, ascender, cap height, x-height, descender, italic angle)]."""
    masters = list(package.masters)
    angles = italic_angles(package, masters)
    rows = []
    for master in masters:
        metrics = fontlab.FontMetrics(package, master)
        rows.append((master, location_text(package, master)) +
                    tuple(float(getattr(metrics, attr)) for _, attr in METRICS) + (angles[master],))
    return rows


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


class Overview(SampleDialog):
    ACTION = None

    def build(self):
        self.setMinimumWidth(680)
        headers = ["Master", "Location"] + [label for label, _ in METRICS] + ["Italic angle"]
        self.table = make_table(headers, 200)
        self.table.horizontalHeader().setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        self.root.addWidget(self.table, 1)
        self._connect(self.table.cellDoubleClicked, lambda row, column, *a: self.make_current(row))
        hint = QtGui.QLabel("Double-click a master to make it current. Values that differ between masters are highlighted.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {muted(self)};")
        self.root.addWidget(hint)

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.rows = []
            return
        self.rows = overview(self.package)
        axes = ", ".join(f"{a.name} ({a.tag})" for a in self.package.axes) or "no axes"
        self.subtitle.setText(f"{len(self.rows)} masters · {axes}")
        varies = {c for c in range(2, 7) if len({row[c] for row in self.rows}) > 1}
        cells = [(r[0], r[1]) + tuple(f"{v:g}" for v in r[2:6]) + (f"{r[6]:g}°",) for r in self.rows]
        fill_table(self.table, cells, lambda r, c, text: c in varies)
        current = self.package.master
        for row, cells_row in enumerate(cells):
            if cells_row[0] == current:
                item = self.table.item(row, 0)
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setText(cells_row[0] + "  (current)")
        self.status.setText(f"Current master: {current}")

    def make_current(self, row):
        master = self.rows[row][0]
        self.package.setMaster(master, True)
        fontlab.UpdateAll()
        self.refresh()


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = Overview(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
