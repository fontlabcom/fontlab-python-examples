#FLM: Generators · Placeholder Glyphs
# this_file: samples/generate_placeholder_glyphs.py
"""Create empty placeholder glyphs from pasted glyph names or characters, on every master.

Names and characters may be separated by spaces, commas or new lines. A single character
becomes uniXXXX (or uXXXXX) with that code point; names of that form also get their code
point unless another glyph already has it. Each master layer gets the chosen advance and
no outlines. Existing glyphs and repeated entries are skipped and listed.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Placeholder Glyphs"
KEY = "generate_placeholder_glyphs"
NAME = re.compile(r"[A-Za-z_.][A-Za-z0-9_.-]*")
UNI = re.compile(r"(?:uni([0-9A-F]{4})|u([0-9A-F]{5,6}))")


# ---------------------------------------------------------------- input
def char_name(char):
    code = ord(char)
    return f"uni{code:04X}" if code <= 0xFFFF else f"u{code:X}"


def code_of(name):
    """The code point a uniXXXX / uXXXXX name stands for, else None."""
    match = UNI.fullmatch(name)
    return int(match.group(1) or match.group(2), 16) if match else None


def parse(text):
    """[(entry, name, problem)]: one row per token; repeated names and invalid tokens carry a problem."""
    rows, seen = [], set()
    for token in re.split(r"[\s,]+", text.strip()):
        if not token:
            continue
        name = char_name(token) if len(token) == 1 and not token.isascii() else token
        if not NAME.fullmatch(name):
            rows.append((token, name, "invalid name"))
        elif name in seen:
            rows.append((token, name, "repeated"))
        else:
            seen.add(name)
            rows.append((token, name, ""))
    return rows


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def used_codes():
    """{code point: glyph name} of the current font."""
    font = fontlab.CurrentFont()
    return {code: g.name for g in (font.glyphs if font is not None else []) for code in g.unicodes}


def create(package, plan, advance):
    """plan: [(name, code or None)]. Adds glyphs, then an empty layer per master at `advance`."""
    made, touched = [], []
    for name, code in plan:
        glyph = fontlab.flGlyph()
        glyph.name = name
        package.addGlyph(glyph)
        glyph = package.findName(name)  # layers exist only on the registered glyph
        for master in package.masters:
            layer = glyph.findLayerCreate(master)
            layer.advanceWidth = advance
            touched.append(layer)
        if code is not None:
            glyph.fgGlyph.unicodes = [code]
        made.append(glyph)
    if made:
        fontlab.flItems().notifyChangesApplied(TITLE, touched + made)
        fontlab.UpdateAll()
    return {"glyphs": len(made), "layers": len(touched)}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Placeholders(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(560)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView, QPlainTextEdit { color: %s }" % ink.name())
        self._connections = []
        self.plan = []
        self.last_result = None
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []

        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        face = heading.font
        face.setPointSizeF(face.pointSizeF() * 1.35)
        face.setBold(True)
        heading.setFont(face)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)

        self.names = QtGui.QPlainTextEdit()
        self.names.setPlaceholderText("e.g.  A.alt  ampersand.ss01  Ω  ₿")
        self.names.setMaximumHeight(90)
        root.addWidget(self.names)
        form = QtGui.QGridLayout()
        self.advance = QtGui.QSpinBox()
        self.advance.setRange(0, 4000)
        self.advance.setSuffix(" units")
        self.advance.setValue(600)
        form.addWidget(QtGui.QLabel("Advance width"), 0, 0)
        form.addWidget(self.advance, 0, 1)
        form.setColumnStretch(2, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Glyph", "Unicode", "Action"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(200)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setAutoDefault(False)
        self.apply_button = QtGui.QPushButton("Create")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.names.textChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal, slot):
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:  # an exception escaping a PythonQt slot can take FontLab down
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def build_plan(self):
        """[(name, code or None, unicode note, problem)] for the pasted entries."""
        codes = used_codes()
        rows = []
        for entry, name, problem in parse(self.names.toPlainText()):
            code = code_of(name)
            note = f"U+{code:04X}" if code is not None else ""
            if not problem and self.package.findName(name) is not None:
                problem = "exists"
            if code is not None and code in codes:
                note += f" (on {codes[code]}, not assigned)"
                code = None
            rows.append((name, code, note, problem))
        return rows

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.plan = []
        else:
            self.subtitle.setText(f"Creates empty glyphs on all {len(self.masters)} masters. "
                                  "Paste names or characters below; existing glyphs are never overwritten.")
            self.plan = self.build_plan()
        ink = QtGui.QBrush(QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText)))
        self.table.setRowCount(len(self.plan))
        for row, (name, code, note, problem) in enumerate(self.plan):
            action = f"{problem}, skipped" if problem else f"create · {len(self.masters)} masters"
            for column, text in enumerate((name, note, action)):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(ink)
                self.table.setItem(row, column, item)
        ready = sum(1 for row in self.plan if not row[3])
        self.apply_button.setEnabled(ready > 0)
        self.status.setText(f"{ready} glyph{'s' if ready != 1 else ''} to create · {len(self.plan) - ready} skipped")

    def apply(self):
        self.refresh()
        ready = [(name, code) for name, code, note, problem in self.plan if not problem]
        self.last_result = create(self.package, ready, self.advance.value)
        self.refresh()
        self.status.setText(f"Created {self.last_result['glyphs']} glyphs ({self.last_result['layers']} master layers)")

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
    dialog = Placeholders(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
