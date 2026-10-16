#FLM: Names · Glyph Finder
# this_file: samples/names_glyph_finder.py
"""Type to find glyphs by name, character or code point; Enter selects them in the Font window.

Accepts a name fragment (acute), a wildcard pattern (*.ss0?), a character
(é), or a code point (U+00E9, 0x1E82, uni00E9). The list updates as you
type; double-click a row to select just that glyph. Nothing in the font
changes.
"""

import fnmatch
import re
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Glyph Finder"
KEY = "names_glyph_finder"
MAX_ROWS = 3000
CODE = re.compile(r"^(?:U\+|u\+|0x|0X|uni|u)([0-9A-Fa-f]{4,6})$")


# ---------------------------------------------------------------- font access
def font_glyphs():
    """[(name, [code points])] for the current font, in font order."""
    font = fontlab.CurrentFont()
    return [(g.name, list(g.unicodes)) for g in font.glyphs] if font is not None else []


def select_in_font_window(names):
    """Replace the Font window selection with `names`; returns how many were selected."""
    import FL

    font = FL.fl.font
    wanted = set(names)
    FL.fl.Unselect()
    count = 0
    for i in range(len(font)):
        if font[i].name in wanted:
            FL.fl.Select(i)
            count += 1
    fontlab.UpdateAll()
    return count


# ---------------------------------------------------------------- core
def matcher(query):
    """(kind, test(name, codes) -> bool) for a query string."""
    query = query.strip()
    code = CODE.match(query)
    if code:
        value = int(code.group(1), 16)
        return "code point", lambda name, codes: value in codes
    if len(query) == 1 and not query.isalnum() or len(query) == 1 and ord(query) > 127:
        value = ord(query)
        return "character", lambda name, codes: value in codes
    if any(c in query for c in "*?["):
        return "pattern", lambda name, codes: fnmatch.fnmatchcase(name, query)
    lowered = query.lower()
    if len(query) == 1:
        value = ord(query)
        return "name or character", lambda name, codes: value in codes or lowered in name.lower()
    return "name", lambda name, codes: lowered in name.lower()


def find(glyphs, query):
    """(kind, [(name, codes)]) matching the query; everything for an empty query."""
    if not query.strip():
        return "all", list(glyphs)
    kind, test = matcher(query)
    return kind, [(name, codes) for name, codes in glyphs if test(name, codes)]


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Finder(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(480)
        self.resize(500, 560)
        self._connections = []
        self.glyphs = font_glyphs()
        self.matches = []

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

        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("acute · *.ss0? · é · U+00E9")
        self.search.setClearButtonEnabled(True)
        big = self.search.font
        big.setPointSizeF(big.pointSizeF() * 1.15)
        self.search.setFont(big)
        root.addWidget(self.search)

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Glyph", "Char", "Unicode"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select in Font window")
        self.close_button.setAutoDefault(False)
        self.select_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.search.textChanged, lambda *a: self.refresh())
        self._connect(self.search.returnPressed, lambda *a: self.select_matches())
        self._connect(self.table.cellDoubleClicked, lambda row, *a: self.select_row(row))
        self._connect(self.select_button.clicked, lambda *a: self.select_matches())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()
        self.search.setFocus()

    def _connect(self, signal, slot):
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:  # an exception escaping a PythonQt slot can take FontLab down
                self.slot_error = repr(error)
                label = getattr(self, "status", None)
                if label is not None:
                    label.setText("Error: " + self.slot_error)
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def refresh(self):
        if not self.glyphs:
            self.subtitle.setText("Open a font first.")
            self.select_button.setEnabled(False)
            return
        kind, self.matches = find(self.glyphs, self.search.text)
        self.subtitle.setText(f"Searching {len(self.glyphs)} glyphs by {kind}. "
                              "Enter selects every match in the Font window.")
        shown = self.matches[:MAX_ROWS]
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(shown))
        for row, (name, codes) in enumerate(shown):
            char = "".join(chr(c) for c in codes[:1])
            cells = [name, char, " ".join(f"U+{c:04X}" for c in codes) or "–"]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column == 1:
                    item.setTextAlignment(int(QtCore.Qt.AlignCenter))
                    item.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, column, item)
        more = f" (showing {MAX_ROWS})" if len(self.matches) > MAX_ROWS else ""
        self.select_button.setEnabled(bool(self.matches))
        self.status.setText(f"{len(self.matches)} match{'es' if len(self.matches) != 1 else ''}{more}")

    def select_matches(self):
        rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()})
        names = [self.matches[r][0] for r in rows] if rows else [name for name, _ in self.matches]
        count = select_in_font_window(names)
        self.last_result = {"selected": names}
        self.status.setText(f"Selected {count} glyph{'s' if count != 1 else ''} in the Font window")

    def select_row(self, row):
        if 0 <= row < len(self.matches):
            count = select_in_font_window([self.matches[row][0]])
            self.last_result = {"selected": [self.matches[row][0]]}
            self.status.setText(f"Selected {self.matches[row][0]}" if count else "Glyph not found")

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
    dialog = Finder(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
