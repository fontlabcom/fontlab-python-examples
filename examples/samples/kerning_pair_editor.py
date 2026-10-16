#FLM: Kerning · Pair Editor
# this_file: samples/kerning_pair_editor.py
"""Edit every kerning pair that involves one glyph, with one column per master.

Rows are the pairs where the glyph, or a kerning class it belongs to, is on the left or right.
Type a new value in any master's cell; clear a cell to delete that pair on that master. Edited
cells turn the accent colour until Apply, which writes all of them as one Undo step. Add a row
for a new partner with the field under the table.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Kerning Pair Editor"
KEY = "kerning_pair_editor"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def current_glyph_name(package):
    """First glyph selected in the Font window, else the current glyph."""
    try:
        import FL

        font = FL.fl.font
        for i in range(len(font)):
            if FL.fl.Selected(i):
                return font[i].name
    except Exception:
        pass
    glyph = fontlab.CurrentGlyph()
    return glyph.name if glyph is not None else None


def kerning_pairs(package, master):
    """{(left, right): value} of one master; class sides are written '@name'."""
    pairs = {}
    for pair, value in package.kerning(master).items():
        left = ("@" if pair.left.mode == "groupMode" else "") + pair.left.id
        right = ("@" if pair.right.mode == "groupMode" else "") + pair.right.id
        pairs[(left, right)] = value
    return pairs


def class_sides(package, master, glyph):
    """('@left class' or None, '@right class' or None) containing the glyph."""
    left = right = None
    for name, (members, mode) in package.kerning(master).groups.items():
        if glyph in members:
            if mode in ("KernLeft", "KernBothSide") and left is None:
                left = "@" + name
            if mode in ("KernRight", "KernBothSide") and right is None:
                right = "@" + name
    return left, right


def native_side(name):
    return (name[1:], True) if name.startswith("@") else (name, False)


def write_kerning(package, edits):
    """Apply {master: {(left, right): value or None}} as one Undo step (None deletes the pair)."""
    items = [package, package.mastersContainer(), package.kerningContainer()]
    package.checkInitHistoryState(0)
    fontlab.flItems.notifyChangesApplied(TITLE, items)
    for master, pairs in edits.items():
        kerning = package.kerning(master)
        for (left, right), value in pairs.items():
            key = (native_side(left), native_side(right))
            if value is None:
                kerning.remove(key)
            else:
                kerning.set(key, int(value))
    fontlab.flItems.notifyChangesApplied(TITLE, items)


# ---------------------------------------------------------------- core
def involving(package, masters, glyph):
    """{(left, right): {master: value}} for pairs whose left or right side is the glyph or its class."""
    rows = {}
    for master in masters:
        left_class, right_class = class_sides(package, master, glyph)
        mine = {glyph, left_class} - {None}, {glyph, right_class} - {None}
        for (left, right), value in kerning_pairs(package, master).items():
            if left in mine[0] or right in mine[1]:
                rows.setdefault((left, right), {})[master] = value
    return rows


def parse_cell(text):
    """int value, None for an empty cell (delete), or raise ValueError."""
    text = text.strip().replace("−", "-")
    if not text:
        return None
    return int(round(float(text)))


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class PairEditor(QtGui.QDialog):
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
        self.resize(600, 620)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.glyph = current_glyph_name(self.package) if self.package else None
        self.rows = {}
        self.order = []
        self.staged = {}
        self.filling = False
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

        self.table = QtGui.QTableWidget(0, len(self.masters) + 1)
        self.table.setHorizontalHeaderLabels(["Pair"] + self.masters)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(260)
        root.addWidget(self.table, 1)

        add = QtGui.QHBoxLayout()
        add.setSpacing(8)
        self.side = QtGui.QComboBox()
        self.side.addItem(f"{self.glyph or '…'}  +  partner")
        self.side.addItem(f"partner  +  {self.glyph or '…'}")
        self.partner = QtGui.QLineEdit()
        self.partner.setPlaceholderText("Partner glyph or @class")
        self.add_button = QtGui.QPushButton("Add row")
        add.addWidget(QtGui.QLabel("New pair"))
        add.addWidget(self.side)
        add.addWidget(self.partner, 1)
        add.addWidget(self.add_button)
        root.addLayout(add)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.revert_button = QtGui.QPushButton("Revert")
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.revert_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.table.itemChanged, lambda item: self.cell_edited(item))
        self._connect(self.add_button.clicked, lambda *a: self.add_row())
        self._connect(self.partner.returnPressed, lambda *a: self.add_row())
        self._connect(self.revert_button.clicked, lambda *a: self.load())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.load()

    def _connect(self, signal, slot):
        def guarded(*args):
            # An exception escaping a PythonQt slot can take FontLab down: report it instead.
            try:
                return slot(*args)
            except Exception as error:
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def load(self):
        self.staged = {}
        self.rows = involving(self.package, self.masters, self.glyph) if self.package and self.glyph else {}
        self.order = sorted(self.rows, key=lambda p: (p[0] != self.glyph and not p[0].startswith("@"), p))
        self.fill()

    def fill(self):
        """Rebuild the table (never called from inside its own itemChanged signal)."""
        self.filling = True
        self.table.setRowCount(len(self.order))
        for row, pair in enumerate(self.order):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(f"{pair[0]}  {pair[1]}"))
            for column, master in enumerate(self.masters, 1):
                value = self.rows.get(pair, {}).get(master)
                item = QtGui.QTableWidgetItem("" if value is None else f"{value:g}")
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
        self.filling = False
        self.refresh()

    def cell_edited(self, item):
        if self.filling:
            return
        if item.column() == 0:  # the pair label is not data: put it back
            self.filling = True
            pair = self.order[item.row()]
            item.setText(f"{pair[0]}  {pair[1]}")
            self.filling = False
            return
        pair, master = self.order[item.row()], self.masters[item.column() - 1]
        try:
            value = parse_cell(item.text())
        except ValueError:
            self.status.setText(f"“{item.text()}” is not a number")
            return
        if value == self.rows.get(pair, {}).get(master):
            self.staged.pop((pair, master), None)
        else:
            self.staged[(pair, master)] = value
        self.refresh()

    def set_cell(self, left, right, master, text):
        """Type into a cell, as a user would (used by tests and handy from the console)."""
        row, column = self.order.index((left, right)), self.masters.index(master) + 1
        self.table.item(row, column).setText(text)

    def add_row(self):
        partner = self.partner.text.strip()
        if not partner or self.glyph is None:
            return
        name = partner[1:] if partner.startswith("@") else partner
        exists = (partner.startswith("@") and name in dict(self.package.kerning(self.masters[0]).groups.items())) or \
                 (not partner.startswith("@") and self.package.findName(name) is not None)
        if not exists:
            self.status.setText(f"No glyph or class named “{partner}”")
            return
        pair = (self.glyph, partner) if self.side.currentIndex == 0 else (partner, self.glyph)
        if pair not in self.order:
            self.order.append(pair)
            self.fill()
        self.partner.setText("")

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif self.glyph is None:
            self.subtitle.setText("Select a glyph in the Font window, then run this script again.")
        else:
            left, right = class_sides(self.package, self.masters[0], self.glyph)
            classes = ", ".join(c for c in (left, right) if c) or "no kerning class"
            self.subtitle.setText(f"Pairs with {self.glyph} ({classes}) on either side. Empty cell = no pair; "
                                  "clear a cell to delete that pair.")
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        plain = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        self.filling = True
        for row, pair in enumerate(self.order):
            for column, master in enumerate(self.masters, 1):
                item = self.table.item(row, column)
                if item is None:
                    continue
                staged = (pair, master) in self.staged
                bold = item.font()
                bold.setBold(staged)
                item.setFont(bold)
                item.setForeground(QtGui.QBrush(accent if staged else plain))
        self.filling = False
        count = len(self.staged)
        self.status.setText(f"{count} edited cell{'s' if count != 1 else ''}" if count else f"{len(self.order)} pairs")
        self.apply_button.setEnabled(bool(count))
        self.revert_button.setEnabled(bool(count))

    def apply(self):
        edits = {}
        for (pair, master), value in self.staged.items():
            edits.setdefault(master, {})[pair] = value
        write_kerning(self.package, edits)
        self.last_result = {m: len(p) for m, p in edits.items()}
        fontlab.UpdateAll()
        self.load()
        self.status.setText(f"Wrote {sum(self.last_result.values())} cells in {len(edits)} masters")

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
    dialog = PairEditor(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
