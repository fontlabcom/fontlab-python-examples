#FLM: Kerning · Missing Pairs
# this_file: samples/kerning_missing_pairs.py
"""List the combinations of two glyph groups that no kerning pair covers on a master.

Enter left and right glyphs: names separated by spaces, plain characters (“AVT”), or @class
tokens that stand for all their members. Every left + right combination that neither a glyph
pair nor a class pair reaches is listed, ready to proof or to kern. "Copy list" puts the
missing pairs on the clipboard, one "left right" per line. Nothing is edited.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Missing Kerning Pairs"
KEY = "kerning_missing_pairs"


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


def class_lists(package, master):
    """({glyph: ['@class', …]} for left sides, the same for right sides, {name: members})."""
    left, right, members = {}, {}, {}
    for name, (glyphs, mode) in package.kerning(master).groups.items():
        members[name] = list(glyphs)
        for glyph in glyphs:
            if mode in ("KernLeft", "KernBothSide"):
                left.setdefault(glyph, []).append("@" + name)
            if mode in ("KernRight", "KernBothSide"):
                right.setdefault(glyph, []).append("@" + name)
    return left, right, members


# ---------------------------------------------------------------- core
def parse_glyphs(text, package, members):
    """Glyph names from 'names', 'characters' and '@class' tokens, unique, in order."""
    out = []
    for token in text.split():
        if token.startswith("@") and token[1:] in members:
            names = members[token[1:]]
        elif package.findName(token) is not None:
            names = [token]
        else:
            names = [g.name for g in (package.findUnicode(ord(c)) for c in token) if g is not None]
        out += [n for n in names if n not in out]
    return out


def covered(pairs, left_classes, right_classes, left, right):
    """True when a glyph or class pair applies to left + right."""
    lefts = [left] + left_classes.get(left, [])
    rights = [right] + right_classes.get(right, [])
    return any((a, b) in pairs for a in lefts for b in rights)


def missing(package, master, lefts, rights):
    pairs = kerning_pairs(package, master)
    left_classes, right_classes, _ = class_lists(package, master)
    return [(l, r) for l in lefts for r in rights if not covered(pairs, left_classes, right_classes, l, r)]


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class MissingPairs(QtGui.QDialog):
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
        self.resize(600, 600)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.lefts, self.rights, self.missing = [], [], []
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

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.left_text = QtGui.QLineEdit("AFLPTVWY")
        self.left_text.setPlaceholderText("Left glyphs: names, characters or @class")
        self.right_text = QtGui.QLineEdit("aeosuy")
        self.right_text.setPlaceholderText("Right glyphs: names, characters or @class")
        self.master = QtGui.QComboBox()
        for name in self.masters:
            self.master.addItem(name)
        if self.current_master in self.masters:
            self.master.setCurrentIndex(self.masters.index(self.current_master))
        form.addWidget(QtGui.QLabel("Left"), 0, 0)
        form.addWidget(self.left_text, 0, 1)
        form.addWidget(QtGui.QLabel("Right"), 1, 0)
        form.addWidget(self.right_text, 1, 1)
        form.addWidget(QtGui.QLabel("Master"), 2, 0)
        form.addWidget(self.master, 2, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Left", "Right"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(220)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.copy_button = QtGui.QPushButton("Copy list")
        self.copy_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.copy_button)
        root.addLayout(footer)

        for line in (self.left_text, self.right_text):
            self._connect(line.textChanged, lambda *a: self.refresh())
        self._connect(self.master.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.copy_button.clicked, lambda *a: self.copy())
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

    def chosen_master(self):
        return self.masters[self.master.currentIndex] if self.masters else ""

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        _, _, members = class_lists(self.package, self.chosen_master())
        self.lefts = parse_glyphs(self.left_text.text, self.package, members)
        self.rights = parse_glyphs(self.right_text.text, self.package, members)
        self.missing = missing(self.package, self.chosen_master(), self.lefts, self.rights)
        combos = len(self.lefts) * len(self.rights)
        self.subtitle.setText(f"{len(self.lefts)} left × {len(self.rights)} right glyphs = {combos} combinations on "
                              f"{self.chosen_master()}; listed are those no glyph or class pair covers.")
        self.table.setRowCount(len(self.missing))
        for row, (left, right) in enumerate(self.missing):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(left))
            self.table.setItem(row, 1, QtGui.QTableWidgetItem(right))
        share = f" ({100 * len(self.missing) // combos} %)" if combos else ""
        self.status.setText(f"{len(self.missing)} of {combos} combinations unkerned{share}")
        self.copy_button.setEnabled(bool(self.missing))

    def copy(self):
        text = "\n".join(f"{l} {r}" for l, r in self.missing)
        QtGui.QApplication.clipboard().setText(text)
        self.status.setText(f"Copied {len(self.missing)} pairs to the clipboard")
        return text

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
    dialog = MissingPairs(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
