#FLM: OpenType · Ligature Recipe Finder
# this_file: samples/features_ligature_finder.py
"""Find underscore-named glyphs and existing input glyphs. Name-derived recipes do not imply outline components.

Standalone PythonQt tool; feature data is shared by all masters.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui


def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def glyph_names():
    font = fontlab.CurrentFont()
    return sorted(g.name for g in font.glyphs) if font is not None else []


def safe_name(name):
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.\-]*|\.notdef", name))  # FEA names may contain hyphens


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
    color.setAlpha(160)
    return color.name(QtGui.QColor.HexArgb)

TITLE = 'Ligature Recipe Finder'
KEY = "features_ligature_finder"
SUBTITLE = 'Find underscore-named glyphs and existing input glyphs. Name-derived recipes do not imply outline components.'
ACTION = 'Copy liga snippet'


def run(names):
    known = set(names)
    rows = []
    for name in sorted(known):
        if "_" not in name or name.startswith("."):
            continue
        stem, separator, suffix = name.partition(".")
        parts = [part + (separator + suffix if separator else "") for part in stem.split("_")]
        missing = [part for part in parts if not part or part not in known]
        valid = not missing and safe_name(name) and all(safe_name(part) for part in parts)
        rows.append((name, " ".join(parts), "Ready" if valid else "Missing / invalid input: " + ", ".join(p or "(empty)" for p in missing)))
    return rows


def liga_text(rows):
    rules = ["    sub " + inputs + " by " + name + ";" for name, inputs, state in rows if state == "Ready"]
    return "feature liga {\n" + "\n".join(rules) + "\n} liga;" if rules else ""


class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self._connections = []
        self.package = current_package()
        self.font_data = fontlab.CurrentFont() if self.package else None
        self.names = glyph_names() if self.package else []
        self.last_result = None
        self.setWindowTitle(TITLE)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self.setMinimumWidth(640)
        self.resize(780, 620)
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel(SUBTITLE if self.package else "Open a font, then run this script again.")
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet("color: " + muted(self))
        root.addWidget(self.subtitle)
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet("color: " + muted(self))
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("Filter ligature names or input glyphs…")
        root.addWidget(self.search)
        self.table = self.make_table(["Ligature glyph", "Input glyphs", "Recipe status"])
        root.addWidget(self.table, 1)
        self.code = QtGui.QPlainTextEdit()
        self.code.setReadOnly(True)
        root.addWidget(self.code, 1)
        self.all_rows = run(self.names)
        self._connect(self.search.textChanged, lambda *a: self.refresh())
        footer = QtGui.QHBoxLayout()
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.close_button)
        self.apply_button = QtGui.QPushButton(ACTION)
        self.apply_button.setDefault(True)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._safe(self.refresh)

    def _safe(self, callback):
        try:
            callback()
        except Exception as error:
            self.status.setText(str(error))
            self.apply_button.setEnabled(False)

    def _connect(self, signal, slot):
        # Keep a plain Python receiver and contain every signal exception.
        wrapped = lambda *args: self._safe(lambda: slot(*args))
        signal.connect(wrapped)
        self._connections.append((signal, wrapped))

    def make_table(self, headers):
        table = QtGui.QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        table.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        return table

    def fill(self, rows):
        self.rows = rows
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, value in enumerate(cells):
                item = QtGui.QTableWidgetItem(str(value))
                if isinstance(value, int):
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)

    def copy_text(self, text):
        QtGui.QApplication.clipboard().setText(text)
        self.last_result = {"copied": text}
        self.status.setText("Copied feature code to the clipboard.")
    def refresh(self):
        needle = self.search.text.lower()
        self.fill([row for row in self.all_rows if needle in " ".join(row).lower()])
        self.snippet = liga_text(self.rows)
        self.code.setPlainText(self.snippet or "No usable underscore recipes in this view.")
        self.apply_button.setEnabled(bool(self.snippet))
        self.status.setText(f"{len(self.rows)} candidates · {sum(row[2] == 'Ready' for row in self.rows)} usable recipes")

    def apply(self):
        if self.snippet:
            self.copy_text(self.snippet)

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        windows = sys.__dict__.get("_fontlab_samples", {})
        if windows.get(KEY) is self:
            windows.pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = Dialog(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
