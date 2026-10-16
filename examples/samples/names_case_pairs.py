#FLM: Names · Case Pairs
# this_file: samples/names_case_pairs.py
"""Find the upper- or lowercase counterparts of the selected glyphs and select them.

Counterparts come from Unicode case mapping of each glyph's code point;
unencoded alternates use their base name (a.ss01 -> A.ss01). Select the
counterparts alone or together with the originals. Nothing in the font
changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Case Pairs"
KEY = "names_case_pairs"


# ---------------------------------------------------------------- font access
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


def font_glyphs():
    """[(name, [code points])] for the current font, in font order."""
    font = fontlab.CurrentFont()
    return [(g.name, list(g.unicodes)) for g in font.glyphs] if font is not None else []


def select_in_font_window(names):
    import FL

    font = FL.fl.font
    wanted = set(names)
    FL.fl.Unselect()
    for i in range(len(font)):
        if font[i].name in wanted:
            FL.fl.Select(i)
    fontlab.UpdateAll()
    return [font[i].name for i in range(len(font)) if FL.fl.Selected(i)]


# ---------------------------------------------------------------- core
def swap_case(char):
    """The single-character case counterpart, or "" (ß -> SS has no single counterpart)."""
    other = char.lower() if char != char.lower() else char.upper()
    return other if len(other) == 1 and other != char else ""


def index(glyphs):
    """(codes by name, first glyph by code) for fast lookups."""
    by_code = {}
    for glyph, codes in glyphs:
        for code in codes:
            by_code.setdefault(code, glyph)
    return dict(glyphs), by_code


def counterpart(name, codes_of, by_code):
    """(counterpart name or None, how) for one glyph name."""
    codes = codes_of.get(name, [])
    if codes:
        other = swap_case(chr(codes[0]))
        if other and ord(other) in by_code:
            return by_code[ord(other)], f"{chr(codes[0])} → {other}"
        return None, f"{chr(codes[0])} has no counterpart in the font" if other else "no case"
    base, dot, suffix = name.partition(".")
    base_codes = codes_of.get(base, [])
    if dot and base_codes:
        partner, _ = counterpart(base, codes_of, by_code)
        if partner and f"{partner}.{suffix}" in codes_of:
            return f"{partner}.{suffix}", f"via {base} → {partner}"
    return None, "unencoded"


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class CasePairs(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(480)
        self.resize(500, 440)
        self._connections = []
        self.pairs = []

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

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setHorizontalHeaderLabels(["Glyph", "Counterpart", "How"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)
        self.keep = QtGui.QCheckBox("Keep the original glyphs selected too")
        root.addWidget(self.keep)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload selection")
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select counterparts")
        self.select_button.setDefault(True)
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.select_button.clicked, lambda *a: self.select_counterparts())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.reload()

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

    def reload(self):
        glyphs = font_glyphs()
        self.selection = selected_names() if glyphs else []
        codes_of, by_code = index(glyphs)
        self.pairs = [(name,) + counterpart(name, codes_of, by_code) for name in self.selection]
        found = [p for p in self.pairs if p[1]]
        if not glyphs:
            self.subtitle.setText("Open a font first.")
        elif not self.selection:
            self.subtitle.setText("Select glyphs in the Font window, then click Reload selection.")
        else:
            self.subtitle.setText(f"{len(found)} of {len(self.selection)} selected glyphs have a case counterpart "
                                  "in this font.")
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(self.pairs))
        for row, (name, partner, how) in enumerate(self.pairs):
            for column, text in enumerate((name, partner or "–", how)):
                item = QtGui.QTableWidgetItem(text)
                if column == 1 and partner:
                    item.setForeground(QtGui.QBrush(accent))
                if column == 2:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(muted(self))))
                self.table.setItem(row, column, item)
        self.select_button.setEnabled(bool(found))
        self.status.setText(f"{len(found)} counterpart{'s' if len(found) != 1 else ''}")

    def select_counterparts(self):
        names = [p[1] for p in self.pairs if p[1]]
        if self.keep.isChecked():
            names += self.selection
        selected = select_in_font_window(names)
        self.last_result = {"selected": selected}
        self.status.setText(f"Selected {len(selected)} glyph{'s' if len(selected) != 1 else ''}")

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
    dialog = CasePairs(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
