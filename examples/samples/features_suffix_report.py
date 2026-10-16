#FLM: OpenType · Suffix Feature Report
# this_file: samples/features_suffix_report.py
"""Suffix inventory across the whole font. Suggestions are naming hints; review the generated code.

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


def suffix_pairs(names, suffix):
    suffix = suffix.lstrip(".")
    known = set(names)
    ending = "." + suffix
    return [(name[:-len(ending)], name) for name in sorted(known)
            if suffix and name.endswith(ending) and name[:-len(ending)] in known
            and safe_name(name) and safe_name(name[:-len(ending)])]


def feature_text(tag, pairs):
    if not re.fullmatch(r"[A-Za-z0-9]{4}", tag):
        raise ValueError("Feature tag must contain four ASCII letters or digits.")
    lines = ["    sub " + base + " by " + target + ";"
             for base, target in pairs]
    return "feature " + tag + " {\n" + "\n".join(lines) + "\n} " + tag + ";"


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
    color.setAlpha(160)
    return color.name(QtGui.QColor.HexArgb)

TITLE = 'Suffix Feature Report'
KEY = "features_suffix_report"
SUBTITLE = 'Suffix inventory across the whole font. Suggestions are naming hints; review the generated code.'
ACTION = 'Copy snippet'


SUGGESTIONS = {"sc": "smcp", "smcp": "smcp", "c2sc": "c2sc", "case": "case",
               "alt": "salt", "liga": "liga", "sups": "sups", "subs": "subs",
               "onum": "onum", "pnum": "pnum", "tnum": "tnum", "numr": "numr", "dnom": "dnom",
               "sinf": "sinf", "ordn": "ordn", "zero": "zero", "osf": "onum", "lf": "lnum",
               "tf": "tnum", "tosf": "onum", "frac": "frac", "init": "init", "medi": "medi",
               "fina": "fina", "isol": "isol"}


def suggested_tag(suffix):
    if re.fullmatch(r"ss(0[1-9]|1[0-9]|20)|cv(0[1-9]|[1-9][0-9])", suffix):
        return suffix
    if re.fullmatch(r"locl[A-Z]{2,3}", suffix):  # e.g. loclPLK: a language-specific form
        return "locl"
    return SUGGESTIONS.get(suffix.split(".")[0], "salt")


def run(names):
    suffixes = sorted({name.split(".", 1)[1] for name in names if "." in name and not name.startswith(".")})
    return [(suffix, sum(n.endswith("." + suffix) for n in names),
             len(suffix_pairs(names, suffix)), suggested_tag(suffix)) for suffix in suffixes]


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
        self.table = self.make_table(["Suffix", "Glyphs", "With base", "Suggested tag"])
        root.addWidget(self.table, 1)
        self.code = QtGui.QPlainTextEdit()
        mono = QtGui.QFont("Menlo")
        mono.setStyleHint(QtGui.QFont.Monospace)
        self.code.setFont(mono)
        self.code.setReadOnly(True)
        root.addWidget(self.code, 1)
        self._connect(self.table.itemSelectionChanged, lambda *a: self.preview())
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
        self.fill(run(self.names))
        if self.rows:
            self.table.selectRow(0)
        self.preview()

    def preview(self):
        row = self.table.currentRow()
        pairs = suffix_pairs(self.names, self.rows[row][0]) if 0 <= row < len(self.rows) else []
        self.snippet = feature_text(self.rows[row][3], pairs) if pairs else ""
        self.code.setPlainText(self.snippet or "No matching base glyphs. Select a suffix with usable pairs.")
        self.apply_button.setEnabled(bool(pairs))
        self.status.setText(f"{len(self.rows)} suffixes · {len(pairs)} safe substitution pairs selected")

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
