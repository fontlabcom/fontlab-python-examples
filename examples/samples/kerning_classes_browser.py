#FLM: Kerning · Classes Browser
# this_file: samples/kerning_classes_browser.py
"""Browse kerning classes: their side, members, and every pair that uses them on each master.

The list on the left shows each class with its side (left = first glyph of a pair, right =
second) and size; filter it by class or member name. Pick a class to see its members and the
pairs that use it with one value column per master. "Select members" selects the class's glyphs
in the Font window. Nothing is edited.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Kerning Classes"
KEY = "kerning_classes_browser"
SIDES = {"KernLeft": "left", "KernRight": "right", "KernBothSide": "both"}


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def kerning_pairs(package, master):
    """{(left, right): value} of one master; class sides are written '@name'."""
    pairs = {}
    for pair, value in package.kerning(master).items():
        left = ("@" if pair.left.mode == "groupMode" else "") + pair.left.id
        right = ("@" if pair.right.mode == "groupMode" else "") + pair.right.id
        pairs[(left, right)] = value
    return pairs


def kerning_classes(package, master):
    """{name: (members, side)} with side 'left', 'right' or 'both'."""
    return {name: (list(members), SIDES.get(mode, mode)) for name, (members, mode) in package.kerning(master).groups.items()}


def select_in_font(names):
    import FL

    font = FL.fl.font
    wanted = set(names)
    for i in range(len(font)):
        FL.fl.Select(i, 1 if font[i].name in wanted else 0)


# ---------------------------------------------------------------- core
def pairs_using(package, masters, name):
    """{(left, right): {master: value}} for pairs with @name on either side."""
    tag, rows = "@" + name, {}
    for master in masters:
        for (left, right), value in kerning_pairs(package, master).items():
            if tag in (left, right):
                rows.setdefault((left, right), {})[master] = value
    return rows


def matches(name, members, text):
    """Class name contains the text (any case), or a member is exactly the text (glyph names are case-sensitive)."""
    text = text.strip()
    return not text or text.lower() in name.lower() or text in members


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class ClassesBrowser(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(720)
        self.resize(780, 560)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.classes = kerning_classes(self.package, self.current_master) if self.package else {}
        self.names = []
        self.selected = None
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

        self.filter = QtGui.QLineEdit()
        self.filter.setPlaceholderText("Filter by class name or member glyph")
        self.filter.setClearButtonEnabled(True)
        root.addWidget(self.filter)

        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.list = QtGui.QListWidget()
        self.list.setAlternatingRowColors(True)
        self.list.setMinimumWidth(220)
        self.splitter.addWidget(self.list)

        detail = QtGui.QWidget()
        side = QtGui.QVBoxLayout(detail)
        side.setContentsMargins(12, 0, 0, 0)
        side.setSpacing(8)
        self.title = QtGui.QLabel()
        title_font = self.title.font
        title_font.setBold(True)
        title_font.setPointSizeF(title_font.pointSizeF() * 1.15)
        self.title.setFont(title_font)
        side.addWidget(self.title)
        self.members = QtGui.QLabel()
        self.members.setWordWrap(True)
        self.members.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        side.addWidget(self.members)
        self.pairs = QtGui.QTableWidget(0, len(self.masters) + 1)
        self.pairs.setHorizontalHeaderLabels(["Pair"] + self.masters)
        self.pairs.verticalHeader().setVisible(False)
        self.pairs.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.pairs.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.pairs.setAlternatingRowColors(True)
        self.pairs.setShowGrid(False)
        header = self.pairs.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.pairs.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        side.addWidget(self.pairs, 1)
        self.splitter.addWidget(detail)
        self.splitter.setStretchFactor(1, 1)
        root.addWidget(self.splitter, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select members")
        self.select_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.filter.textChanged, lambda *a: self.fill())
        self._connect(self.list.currentRowChanged, lambda row: self.show_class(row))
        self._connect(self.select_button.clicked, lambda *a: self.select_members())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.fill()

    def _connect(self, signal, slot):
        def guarded(*args):
            # An exception escaping a PythonQt slot can take FontLab down: report it instead.
            try:
                return slot(*args)
            except Exception as error:
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def fill(self):
        text = self.filter.text
        self.names = sorted(n for n, (members, _) in self.classes.items() if matches(n, members, text))
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            counts = {s: sum(1 for _, side in self.classes.values() if side == s) for s in ("left", "right", "both")}
            self.subtitle.setText(f"{len(self.classes)} classes: {counts['left']} left, {counts['right']} right, "
                                  f"{counts['both']} both sides. Values are shown for all {len(self.masters)} masters.")
        self.list.clear()
        for name in self.names:
            members, side = self.classes[name]
            self.list.addItem(f"@{name}   {side} · {len(members)}")
        self.status.setText(f"{len(self.names)} of {len(self.classes)} classes")
        if self.names:
            self.list.setCurrentRow(0)
        else:
            self.show_class(-1)

    def show_class(self, row):
        if row < 0 or row >= len(self.names):
            self.selected = None
            self.title.setText("No class")
            self.members.setText("")
            self.pairs.setRowCount(0)
            self.select_button.setEnabled(False)
            return
        name = self.names[row]
        members, side = self.classes[name]
        self.selected = name
        self.title.setText(f"@{name} · {side} side")
        self.members.setText(" ".join(members))
        rows = pairs_using(self.package, self.masters, name)
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.pairs.setRowCount(len(rows))
        for r, pair in enumerate(sorted(rows)):
            label = QtGui.QTableWidgetItem(f"{pair[0]}  {pair[1]}")
            self.pairs.setItem(r, 0, label)
            for column, master in enumerate(self.masters, 1):
                value = rows[pair].get(master)
                item = QtGui.QTableWidgetItem("–" if value is None else f"{value:g}")
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if value is None:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(muted(self))))
                self.pairs.setItem(r, column, item)
        self.select_button.setEnabled(True)
        self.status.setText(f"@{name}: {len(members)} members, used in {len(rows)} pairs")
        self.pair_rows = {f"{l} {r}": v for (l, r), v in rows.items()}

    def select_class(self, name):
        """Show a class by name (used by tests and handy from the console)."""
        self.list.setCurrentRow(self.names.index(name))

    def select_members(self):
        if self.selected is None:
            return
        members = self.classes[self.selected][0]
        select_in_font(members)
        fontlab.UpdateAll()
        self.status.setText(f"Selected {len(members)} glyphs of @{self.selected} in the Font window")

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
    dialog = ClassesBrowser(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
