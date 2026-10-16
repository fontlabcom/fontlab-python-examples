#FLM: Outlines · Node Coordinates Panel
# this_file: samples/outlines_node_coordinates_panel.py
"""A small live panel listing the selected nodes of the current glyph with coordinates.

A QTimer polls the selection a few times a second, so the panel follows you while you edit in
the Glyph window: coordinates and type per node, then distance, offsets and angle between each
pair of consecutive selected nodes. Copy puts the list on the clipboard. Read-only.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Node Coordinates"
KEY = "outlines_node_coordinates_panel"
INTERVAL_MS = 400


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


# ---------------------------------------------------------------- core
def current_glyph(package):
    """The glyph being edited (Glyph window), else the Font window's current glyph."""
    glyph = fontlab.flWorkspace.instance().currentGlyph
    if glyph is not None and not glyph.isNull:
        found = package.findName(glyph.name)
        if found is not None:
            return found
    fg = fontlab.CurrentGlyph()
    return package.findName(fg.name) if fg is not None else None


def selected_nodes(layer):
    """[(contour index, node index, x, y, on)] for selected nodes of the layer's own contours."""
    rows = []
    for c, contour in enumerate(own_contours(layer)):
        for n, node in enumerate(contour.nodes()):
            if node.selected:
                rows.append((c, n, node.x, node.y, bool(node.isOn())))
    return rows


def measures(rows):
    """[(label, dx, dy, distance, angle°)] between consecutive selected nodes."""
    result = []
    for a, b in zip(rows, rows[1:]):
        dx, dy = b[2] - a[2], b[3] - a[3]
        result.append((f"{a[0] + 1}:{a[1]} → {b[0] + 1}:{b[1]}", dx, dy, math.hypot(dx, dy),
                       math.degrees(math.atan2(dy, dx))))
    return result


def number(value):
    return f"{value:.1f}".rstrip("0").rstrip(".") if value != int(value) else str(int(value))


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


class NodePanel(SampleDialog):
    ACTION = "Copy"

    def build(self):
        self.setMinimumWidth(440)
        self.signature = None
        self.rows_data = []
        self.nodes = make_table(["Contour : node", "x", "y", "Type"], 160)
        self.root.addWidget(self.nodes, 2)
        caption = QtGui.QLabel("Between consecutive selected nodes")
        caption.setStyleSheet(f"color: {muted(self)};")
        self.root.addWidget(caption)
        self.pairs = make_table(["From → to", "dx", "dy", "Distance", "Angle"], 100)
        self.root.addWidget(self.pairs, 1)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(INTERVAL_MS)
        self._connect(self.timer.timeout, lambda *a: self.tick())
        self.timer.start()

    def tick(self):
        try:
            self.refresh()
        except Exception as error:  # the glyph may vanish between ticks; keep the panel alive
            self.status.setText(f"Paused: {type(error).__name__}")

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        glyph = current_glyph(self.package)
        layer = glyph.findLayer(self.package.master) if glyph is not None else None
        rows = selected_nodes(layer) if layer is not None else []
        signature = (glyph.name if glyph is not None else None, self.package.master, tuple(rows))
        if signature == self.signature:
            return
        self.signature, self.rows_data, self.glyph_name = signature, rows, signature[0]
        if glyph is None:
            self.subtitle.setText("Open a glyph to see its selected nodes.")
        else:
            self.subtitle.setText(f"{glyph.name} · {self.package.master} — select nodes in the Glyph window")
        fill_table(self.nodes, [(f"{c + 1} : {n}", number(x), number(y), "on" if on else "handle")
                                for c, n, x, y, on in rows])
        fill_table(self.pairs, [(label, number(dx), number(dy), f"{d:.1f}", f"{a:.1f}°")
                                for label, dx, dy, d, a in measures(rows)], lambda r, c, text: c == 3)
        self.apply_button.setEnabled(bool(rows))
        self.status.setText(f"{len(rows)} node{'s' if len(rows) != 1 else ''} selected · live, every {INTERVAL_MS} ms")

    def apply(self):
        lines = [f"{c + 1}:{n}\t{number(x)}\t{number(y)}" for c, n, x, y, _ in self.rows_data]
        QtGui.QApplication.clipboard().setText("\n".join(lines))
        self.last_result = {"copied": len(lines)}
        self.status.setText(f"Copied {len(lines)} lines")

    def teardown(self):
        self.timer.stop()


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = NodePanel(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
