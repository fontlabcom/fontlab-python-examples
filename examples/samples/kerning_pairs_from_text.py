#FLM: Kerning · Pairs from Text
# this_file: samples/kerning_pairs_from_text.py
"""Type a word, see each adjacent pair's kerning on every master, and set the ones you tick.

Pairs are taken inside words (spaces separate words; /glyphname tokens work too). The table
shows what FontLab applies now on each master, marking values that come from a class pair.
Set or Add writes explicit glyph pairs for the ticked rows on the chosen masters; one Apply is
one Undo step.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Kerning Pairs from Text"
KEY = "kerning_pairs_from_text"
MODES = [("Set to", "set"), ("Add to current", "add")]


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def explicit_pairs(package, master):
    """{(left, right): value} of glyph-glyph pairs only."""
    pairs = {}
    for pair, value in package.kerning(master).items():
        if pair.left.mode == "glyphMode" and pair.right.mode == "glyphMode":
            pairs[(pair.left.id, pair.right.id)] = value
    return pairs


def write_kerning(package, edits):
    """Apply {master: {(left, right): value}} of glyph pairs as one Undo step."""
    items = [package, package.mastersContainer(), package.kerningContainer()]
    package.checkInitHistoryState(0)
    fontlab.flItems.notifyChangesApplied(TITLE, items)
    for master, pairs in edits.items():
        kerning = package.kerning(master)
        for (left, right), value in pairs.items():
            kerning.set(((left, False), (right, False)), int(value))
    fontlab.flItems.notifyChangesApplied(TITLE, items)


# ---------------------------------------------------------------- core
def parse_words(text, package):
    """[[glyph names]] per word: characters by Unicode, '/name' tokens by name."""
    words = []
    for chunk in text.split():
        names, i = [], 0
        while i < len(chunk):
            if chunk[i] == "/":
                j = chunk.find("/", i + 1)
                j = len(chunk) if j < 0 else j
                token = chunk[i + 1:j]
                if token and package.findName(token) is not None:
                    names.append(token)
                i = j
                continue
            glyph = package.findUnicode(ord(chunk[i]))
            if glyph is not None:
                names.append(glyph.name)
            i += 1
        words.append(names)
    return words


def adjacent_pairs(words):
    """Unique (left, right) pairs in reading order."""
    seen = []
    for names in words:
        for pair in zip(names, names[1:]):
            if pair not in seen:
                seen.append(pair)
    return seen


def current_value(kerning, explicit, pair):
    """(value FontLab applies, True when it comes from an explicit glyph pair)."""
    if pair in explicit:
        return explicit[pair], True
    try:
        value = kerning.get(pair)
    except Exception:
        value = None
    return value or 0, False


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class PairsFromText(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(600)
        self.resize(640, 560)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.pairs = []
        self.values = {}
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

        self.text = QtGui.QLineEdit("AVATAR Type")
        self.text.setPlaceholderText("Words to kern, e.g. AVATAR Type /Aacute/V")
        root.addWidget(self.text)

        self.table = QtGui.QTableWidget(0, len(self.masters) + 1)
        self.table.setHorizontalHeaderLabels(["Pair"] + self.masters)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(220)
        root.addWidget(self.table, 1)

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.mode = QtGui.QComboBox()
        for label, _ in MODES:
            self.mode.addItem(label)
        self.value = QtGui.QSpinBox()
        self.value.setRange(-2000, 2000)
        self.value.setAlignment(QtCore.Qt.AlignRight)
        self.value.setSuffix(" units")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Ticked pairs"), 0, 0)
        form.addWidget(self.mode, 0, 1)
        form.addWidget(self.value, 0, 2)
        form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        form.addWidget(self.scope, 1, 1, 1, 2)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(2, 1)
        root.addLayout(form)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.text.textChanged, lambda *a: self.refresh())
        self._connect(self.table.itemChanged, lambda *a: self.count())
        self._connect(self.mode.currentIndexChanged, lambda *a: self.count())
        self._connect(self.value.valueChanged, lambda *a: self.count())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.count())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal, slot):
        def guarded(*args):
            # An exception escaping a PythonQt slot can take FontLab down: report it instead.
            try:
                return slot(*args)
            except Exception as error:
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def chosen_masters(self):
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def refresh(self, keep_ticks=None):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        self.pairs = adjacent_pairs(parse_words(self.text.text, self.package))
        self.values = {}
        for master in self.masters:
            kerning, explicit = self.package.kerning(master), explicit_pairs(self.package, master)
            for pair in self.pairs:
                self.values[(pair, master)] = current_value(kerning, explicit, pair)
        self.subtitle.setText(f"{len(self.pairs)} pairs from the text. Values are what each master applies now; "
                              "“class” marks values inherited from a class pair.")
        dim = QtGui.QColor(muted(self))
        self.filling = True
        self.table.setRowCount(len(self.pairs))
        for row, pair in enumerate(self.pairs):
            name = QtGui.QTableWidgetItem(f"{pair[0]}  {pair[1]}")
            ticked = keep_ticks is None or pair in keep_ticks
            name.setCheckState(QtCore.Qt.Checked if ticked else QtCore.Qt.Unchecked)
            self.table.setItem(row, 0, name)
            for column, master in enumerate(self.masters, 1):
                value, own = self.values[(pair, master)]
                item = QtGui.QTableWidgetItem(f"{value:g}" if own else (f"{value:g}  class" if value else "–"))
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if not own:
                    item.setForeground(QtGui.QBrush(dim))
                self.table.setItem(row, column, item)
        self.filling = False
        self.count()

    def ticked(self):
        return [self.pairs[r] for r in range(self.table.rowCount)
                if self.table.item(r, 0).checkState() == QtCore.Qt.Checked]

    def tick(self, pairs):
        """Tick exactly these pairs (used by tests and handy from the console)."""
        self.filling = True
        for row, pair in enumerate(self.pairs):
            self.table.item(row, 0).setCheckState(QtCore.Qt.Checked if pair in pairs else QtCore.Qt.Unchecked)
        self.filling = False
        self.count()

    def plan(self):
        add = MODES[self.mode.currentIndex][1] == "add"
        edits = {}
        for master in self.chosen_masters():
            for pair in self.ticked():
                current = self.values[(pair, master)][0]
                edits.setdefault(master, {})[pair] = current + self.value.value if add else self.value.value
        return edits

    def count(self):
        if self.filling:
            return
        edits = self.plan()
        cells = sum(len(p) for p in edits.values())
        self.status.setText(f"{len(self.ticked())} of {len(self.pairs)} pairs ticked · {cells} values to write")
        self.apply_button.setEnabled(bool(cells))

    def apply(self):
        edits = self.plan()
        write_kerning(self.package, edits)
        self.last_result = {m: len(p) for m, p in edits.items()}
        fontlab.UpdateAll()
        self.refresh(keep_ticks=self.ticked())
        self.status.setText(f"Wrote {sum(self.last_result.values())} pair values")

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
    dialog = PairsFromText(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
