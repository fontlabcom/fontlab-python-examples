#FLM: Names · Charset Compare
# this_file: samples/names_charset_compare.py
"""Paste a text or a character set and compare it with the font's encoded characters.

Lists characters of the text the font lacks and characters the font has
that the text does not use, with names from unicodedata. Language presets
fill in common alphabets. Copy the missing set, or select the extra glyphs
in the Font window. Nothing in the font changes.
"""

import sys
import unicodedata

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Charset Compare"
KEY = "names_charset_compare"
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
PRESETS = [
    ("Paste your own text…", ""),
    ("Basic Latin (ASCII)", "".join(chr(c) for c in range(0x21, 0x7F))),
    ("Latin-1 letters", LATIN + "".join(chr(c) for c in range(0xC0, 0x100) if chr(c).isalpha())),
    ("Polish", LATIN + "ĄĆĘŁŃÓŚŹŻąćęłńóśźż"),
    ("Czech", LATIN + "ÁČĎÉĚÍŇÓŘŠŤÚŮÝŽáčďéěíňóřšťúůýž"),
    ("German", LATIN + "ÄÖÜẞäöüß„“‚‘"),
    ("French", LATIN + "ÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸàâæçéèêëîïôœùûüÿ«»"),
    ("Spanish", LATIN + "ÁÉÍÑÓÚÜáéíñóúü¡¿"),
    ("Turkish", LATIN + "ÇĞİÖŞÜçğıöşü"),
]


# ---------------------------------------------------------------- font access
def font_chars():
    """{character: glyph name} for every encoded glyph of the current font."""
    font = fontlab.CurrentFont()
    out = {}
    for glyph in (font.glyphs if font is not None else []):
        for code in glyph.unicodes:
            out.setdefault(chr(code), glyph.name)
    return out


def select_in_font_window(names):
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
def text_chars(text):
    """Distinct non-whitespace characters of the text, sorted by code point."""
    return sorted({c for c in text if not c.isspace()}, key=ord)


def compare(text, available):
    """(missing, extra): characters of the text absent from the font, and font characters absent from it."""
    wanted = text_chars(text)
    wanted_set = set(wanted)
    missing = [c for c in wanted if c not in available]
    extra = sorted((c for c in available if c not in wanted_set and not c.isspace()), key=ord)
    return missing, extra


def describe(char):
    return f"{char}   U+{ord(char):04X}   {unicodedata.name(char, '').title()}"


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class CharsetCompare(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(620)
        self.resize(680, 560)
        self._connections = []
        self.available = font_chars()
        self.missing, self.extra = [], []

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

        row = QtGui.QHBoxLayout()
        row.addWidget(QtGui.QLabel("Preset"))
        self.preset = QtGui.QComboBox()
        for label, _ in PRESETS:
            self.preset.addItem(label)
        row.addWidget(self.preset, 1)
        root.addLayout(row)
        self.text = QtGui.QPlainTextEdit()
        self.text.setPlaceholderText("Paste a text or a list of characters…")
        self.text.setMaximumHeight(90)
        root.addWidget(self.text)

        lists = QtGui.QHBoxLayout()
        lists.setSpacing(12)
        self.missing_label, self.missing_list = self._column(lists)
        self.extra_label, self.extra_list = self._column(lists)
        root.addLayout(lists, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.copy_button = QtGui.QPushButton("Copy missing")
        self.select_button = QtGui.QPushButton("Select extra glyphs")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.copy_button)
        footer.addWidget(self.select_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self._connect(self.preset.currentIndexChanged, lambda *a: self.use_preset(self.preset.currentIndex))
        self._connect(self.text.textChanged, lambda *a: self.refresh())
        self._connect(self.copy_button.clicked, lambda *a: self.copy_missing())
        self._connect(self.select_button.clicked, lambda *a: self.select_extra())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _column(self, parent):
        column = QtGui.QVBoxLayout()
        label = QtGui.QLabel()
        bold = label.font
        bold.setBold(True)
        label.setFont(bold)
        listing = QtGui.QListWidget()
        listing.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        listing.setAlternatingRowColors(True)
        listing.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        listing.setTextElideMode(QtCore.Qt.ElideRight)
        column.addWidget(label)
        column.addWidget(listing, 1)
        parent.addLayout(column, 1)
        return label, listing

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

    def use_preset(self, index):
        if 0 < index < len(PRESETS):
            self.text.setPlainText(PRESETS[index][1])

    def refresh(self):
        text = self.text.toPlainText()
        self.missing, self.extra = compare(text, self.available)
        count = len(text_chars(text))
        if not self.available:
            self.subtitle.setText("Open a font with encoded glyphs first.")
        else:
            self.subtitle.setText(f"The font encodes {len(self.available)} characters; the text uses {count}.")
        self.missing_label.setText(f"Missing from the font ({len(self.missing)})")
        self.extra_label.setText(f"In the font, not in the text ({len(self.extra)})")
        alert = QtGui.QColor("#d33")
        self.missing_list.clear()
        for char in self.missing:
            item = QtGui.QListWidgetItem(describe(char))
            item.setForeground(QtGui.QBrush(alert))
            self.missing_list.addItem(item)
        self.extra_list.clear()
        for char in self.extra:
            self.extra_list.addItem(QtGui.QListWidgetItem(f"{describe(char)}   · {self.available[char]}"))
        self.copy_button.setEnabled(bool(self.missing))
        self.select_button.setEnabled(bool(self.extra) and bool(text.strip()))
        covered = count - len(self.missing)
        self.status.setText(f"Coverage {covered}/{count}" + (f" · {100.0 * covered / count:.0f}%" if count else ""))

    def copy_missing(self):
        QtGui.QApplication.clipboard().setText("".join(self.missing))
        self.status.setText(f"Copied {len(self.missing)} characters")

    def select_extra(self):
        names = [self.available[c] for c in self.extra]
        count = select_in_font_window(names)
        self.last_result = {"selected": names}
        self.status.setText(f"Selected {count} extra glyph{'s' if count != 1 else ''} in the Font window")

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
    dialog = CharsetCompare(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
