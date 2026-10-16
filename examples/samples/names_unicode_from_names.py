#FLM: Names · Unicode from Names
# this_file: samples/names_unicode_from_names.py
"""Assign Unicode code points derived from glyph names, with a preview first.

Understands uniXXXX and uXXXX[XX] names, a small Adobe Glyph List table and
accented Latin names (Wacute -> LATIN CAPITAL LETTER W WITH ACUTE via
unicodedata). Suffixed alternates and ligatures are left alone. A code point
already used by another glyph is reported, never stolen. One Undo step.
"""

import re
import sys
import unicodedata

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Unicode from Names"
KEY = "names_unicode_from_names"
AGL_TEXT = (
    "space 0020 exclam 0021 quotedbl 0022 numbersign 0023 dollar 0024 percent 0025 ampersand 0026 quotesingle 0027 "
    "parenleft 0028 parenright 0029 asterisk 002A plus 002B comma 002C hyphen 002D period 002E slash 002F zero 0030 "
    "one 0031 two 0032 three 0033 four 0034 five 0035 six 0036 seven 0037 eight 0038 nine 0039 colon 003A semicolon "
    "003B less 003C equal 003D greater 003E question 003F at 0040 A 0041 B 0042 C 0043 D 0044 E 0045 F 0046 G 0047 "
    "H 0048 I 0049 J 004A K 004B L 004C M 004D N 004E O 004F P 0050 Q 0051 R 0052 S 0053 T 0054 U 0055 V 0056 W "
    "0057 X 0058 Y 0059 Z 005A bracketleft 005B backslash 005C bracketright 005D asciicircum 005E underscore 005F "
    "grave 0060 a 0061 b 0062 c 0063 d 0064 e 0065 f 0066 g 0067 h 0068 i 0069 j 006A k 006B l 006C m 006D n 006E o "
    "006F p 0070 q 0071 r 0072 s 0073 t 0074 u 0075 v 0076 w 0077 x 0078 y 0079 z 007A braceleft 007B bar 007C "
    "braceright 007D asciitilde 007E exclamdown 00A1 cent 00A2 sterling 00A3 currency 00A4 yen 00A5 brokenbar 00A6 "
    "section 00A7 dieresis 00A8 copyright 00A9 ordfeminine 00AA guillemotleft 00AB logicalnot 00AC registered 00AE "
    "macron 00AF degree 00B0 plusminus 00B1 acute 00B4 mu 00B5 paragraph 00B6 periodcentered 00B7 cedilla 00B8 "
    "ordmasculine 00BA guillemotright 00BB onequarter 00BC onehalf 00BD threequarters 00BE questiondown 00BF Agrave "
    "00C0 Aacute 00C1 Acircumflex 00C2 Atilde 00C3 Adieresis 00C4 Aring 00C5 AE 00C6 Ccedilla 00C7 Egrave 00C8 "
    "Eacute 00C9 Ecircumflex 00CA Edieresis 00CB Igrave 00CC Iacute 00CD Icircumflex 00CE Idieresis 00CF Eth 00D0 "
    "Ntilde 00D1 Ograve 00D2 Oacute 00D3 Ocircumflex 00D4 Otilde 00D5 Odieresis 00D6 multiply 00D7 Oslash 00D8 "
    "Ugrave 00D9 Uacute 00DA Ucircumflex 00DB Udieresis 00DC Yacute 00DD Thorn 00DE germandbls 00DF agrave 00E0 "
    "aacute 00E1 acircumflex 00E2 atilde 00E3 adieresis 00E4 aring 00E5 ae 00E6 ccedilla 00E7 egrave 00E8 eacute "
    "00E9 ecircumflex 00EA edieresis 00EB igrave 00EC iacute 00ED icircumflex 00EE idieresis 00EF eth 00F0 ntilde "
    "00F1 ograve 00F2 oacute 00F3 ocircumflex 00F4 otilde 00F5 odieresis 00F6 divide 00F7 oslash 00F8 ugrave 00F9 "
    "uacute 00FA ucircumflex 00FB udieresis 00FC yacute 00FD thorn 00FE ydieresis 00FF Amacron 0100 amacron 0101 "
    "Abreve 0102 abreve 0103 Aogonek 0104 aogonek 0105 Cacute 0106 cacute 0107 Ccircumflex 0108 ccircumflex 0109 "
    "Cdotaccent 010A cdotaccent 010B Ccaron 010C ccaron 010D Dcaron 010E dcaron 010F Dcroat 0110 dcroat 0111 "
    "Emacron 0112 emacron 0113 Ebreve 0114 ebreve 0115 Edotaccent 0116 edotaccent 0117 Eogonek 0118 eogonek 0119 "
    "Ecaron 011A ecaron 011B Gcircumflex 011C gcircumflex 011D Gbreve 011E gbreve 011F Gdotaccent 0120 gdotaccent "
    "0121 Hcircumflex 0124 hcircumflex 0125 Hbar 0126 hbar 0127 Itilde 0128 itilde 0129 Imacron 012A imacron 012B "
    "Ibreve 012C ibreve 012D Iogonek 012E iogonek 012F Idotaccent 0130 dotlessi 0131 IJ 0132 ij 0133 Jcircumflex "
    "0134 jcircumflex 0135 kgreenlandic 0138 Lacute 0139 lacute 013A Lcaron 013D lcaron 013E Ldot 013F ldot 0140 "
    "Lslash 0141 lslash 0142 Nacute 0143 nacute 0144 Ncaron 0147 ncaron 0148 napostrophe 0149 Eng 014A eng 014B "
    "Omacron 014C omacron 014D Obreve 014E obreve 014F Ohungarumlaut 0150 ohungarumlaut 0151 OE 0152 oe 0153 Racute "
    "0154 racute 0155 Rcaron 0158 rcaron 0159 Sacute 015A sacute 015B Scircumflex 015C scircumflex 015D Scedilla "
    "015E scedilla 015F Scaron 0160 scaron 0161 Tcaron 0164 tcaron 0165 Tbar 0166 tbar 0167 Utilde 0168 utilde 0169 "
    "Umacron 016A umacron 016B Ubreve 016C ubreve 016D Uring 016E uring 016F Uhungarumlaut 0170 uhungarumlaut 0171 "
    "Uogonek 0172 uogonek 0173 Wcircumflex 0174 wcircumflex 0175 Ycircumflex 0176 ycircumflex 0177 Ydieresis 0178 "
    "Zacute 0179 zacute 017A Zdotaccent 017B zdotaccent 017C Zcaron 017D zcaron 017E longs 017F florin 0192 "
    "circumflex 02C6 caron 02C7 breve 02D8 dotaccent 02D9 ring 02DA ogonek 02DB tilde 02DC hungarumlaut 02DD endash "
    "2013 emdash 2014 underscoredbl 2017 quoteleft 2018 quoteright 2019 quotesinglbase 201A quotereversed 201B "
    "quotedblleft 201C quotedblright 201D quotedblbase 201E dagger 2020 daggerdbl 2021 bullet 2022 onedotenleader "
    "2024 twodotenleader 2025 ellipsis 2026 perthousand 2030 minute 2032 second 2033 guilsinglleft 2039 "
    "guilsinglright 203A exclamdbl 203C fraction 2044 Euro 20AC trademark 2122 arrowleft 2190 arrowup 2191 "
    "arrowright 2192 arrowdown 2193 partialdiff 2202 existential 2203 emptyset 2205 Delta 2206 gradient 2207 "
    "element 2208 notelement 2209 suchthat 220B product 220F summation 2211 minus 2212 asteriskmath 2217 radical "
    "221A proportional 221D infinity 221E orthogonal 221F angle 2220 logicaland 2227 logicalor 2228 intersection "
    "2229 integral 222B therefore 2234 similar 223C congruent 2245 approxequal 2248 notequal 2260 equivalence 2261 "
    "lessequal 2264 greaterequal 2265 lozenge 25CA "
    "twosuperior 00B2 threesuperior 00B3 onesuperior 00B9 nbspace 00A0 fi FB01 fl FB02"
)
AGL = dict(zip(AGL_TEXT.split()[0::2], (int(v, 16) for v in AGL_TEXT.split()[1::2])))
ACCENTS = {
    "acute": "ACUTE", "grave": "GRAVE", "circumflex": "CIRCUMFLEX", "dieresis": "DIAERESIS", "tilde": "TILDE",
    "ring": "RING ABOVE", "caron": "CARON", "breve": "BREVE", "macron": "MACRON", "ogonek": "OGONEK",
    "cedilla": "CEDILLA", "dotaccent": "DOT ABOVE", "hungarumlaut": "DOUBLE ACUTE", "commaaccent": "COMMA BELOW",
    "dotbelow": "DOT BELOW", "hookabove": "HOOK ABOVE", "stroke": "STROKE",
}
UNI = re.compile(r"^uni([0-9A-F]{4})$")
U = re.compile(r"^u([0-9A-F]{4,6})$")


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


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


def font_unicodes():
    """{glyph name: [code points]} for the whole current font, in font order."""
    font = fontlab.CurrentFont()
    return {g.name: list(g.unicodes) for g in font.glyphs} if font is not None else {}


# ---------------------------------------------------------------- core
def notify(package, glyphs):
    """One Undo step needs the same [layers + glyphs] list notified before and after the edit."""
    if glyphs:
        layers = [g.findLayer(package.master) or g.layers[0] for g in glyphs]
        layers = [layer for layer in layers if not layer.autoLayer]  # notifying auto layers re-resolves them all
        fontlab.flItems().notifyChangesApplied(TITLE, layers + glyphs)


def code_for_name(name):
    """(code point, source) derived from a glyph name, or (None, "") when the name says nothing."""
    if "." in name[1:] or "_" in name:
        return None, ""
    match = UNI.match(name) or U.match(name)
    if match:
        code = int(match.group(1), 16)
        return (code, name[:3] if name.startswith("uni") else "u") if code <= 0x10FFFF else (None, "")
    if name in AGL:
        return AGL[name], "AGL"
    for accent, words in ACCENTS.items():
        if name.endswith(accent) and len(name) > len(accent):
            base = name[: -len(accent)]
            if len(base) == 1 and base.isalpha():
                case = "CAPITAL" if base.isupper() else "SMALL"
                try:
                    return ord(unicodedata.lookup(f"LATIN {case} LETTER {base.upper()} WITH {words}")), "derived"
                except KeyError:
                    return None, ""
    return None, ""


def plan(names, unicodes, overwrite):
    """[(name, current, code, source, status)]: status "assign", "same" or "used by <glyph>"."""
    owners = {}
    for glyph, codes in unicodes.items():
        for code in codes:
            owners.setdefault(code, glyph)
    rows = []
    for name in names:
        code, source = code_for_name(name)
        current = unicodes.get(name, [])
        if code is None:
            continue
        if code in current:
            status = "same"
        elif current and not overwrite:
            status = "encoded differently"
        elif owners.get(code, name) != name:
            status = f"used by {owners[code]}"
        else:
            status = "assign"
        rows.append((name, current, code, source, status))
    return rows


def run(package, rows):
    """Set the derived code point on every "assign" row; one Undo step. Returns the names changed."""
    plans = [(package.findName(name), code) for name, _current, code, _source, status in rows if status == "assign"]
    plans = [(glyph, code) for glyph, code in plans if glyph is not None]
    changed = [glyph for glyph, _ in plans]
    notify(package, changed)
    for glyph, code in plans:
        glyph.fgGlyph.unicodes = [code]
    notify(package, changed)
    return [g.name for g in changed]


def hexes(codes):
    return " ".join(f"U+{c:04X}" for c in codes) or "–"


# ---------------------------------------------------------------- GUI
def auto_dependants(package, names):
    """Auto composites (any auto master layer) that use one of `names` as a component."""
    wanted = set(names)
    if package is None or not wanted:
        return []
    import FL

    font, found = FL.fl.font, []
    for index in range(len(font)):
        glyph = package.findName(font[index].name)
        if glyph is None or glyph.name in wanted:
            continue
        for layer in glyph.layers:
            if layer.isMasterLayer and layer.autoLayer and any(
                    shape.isComponent and str(shape.shapeData.componentGlyph) in wanted for shape in layer.shapes):
                found.append(glyph.name)
                break
    return found


def rebuild_note(package, names, limit=5):
    """Status text naming the auto composites FontLab rebuilds when their bases are notified (fl#8512)."""
    found = auto_dependants(package, names)
    if not found:
        return ""
    shown = ", ".join(found[:limit]) + (f" +{len(found) - limit} more" if len(found) > limit else "")
    return f"FontLab will rebuild auto {shown} (anchors/locks may change; Undo does not restore them)"


def show_rebuilds(dialog, names):
    """Append the auto composites FontLab will rebuild to the dialog's status: notifying a base of
    auto composites re-resolves auto layers font-wide (AGENTS: editing a BASE of auto composites)."""
    status = getattr(dialog, "status", None)
    note = rebuild_note(dialog.package, names) if status is not None else ""
    if note:
        text = status.text
        status.setText(f"{text} · {note}" if text else note)
        # the wrapped note must not overlap the table: reserve its height, which grows the dialog
        status.setMinimumHeight(status.heightForWidth(max(status.width, 320)))


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class UnicodeFromNames(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(560)
        self._connections = []
        self.rows = []

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
        self.scope = QtGui.QComboBox()
        self.overwrite = QtGui.QCheckBox("Replace a different existing code point")
        form.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        form.addWidget(self.scope, 0, 1)
        form.addWidget(self.overwrite, 1, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Glyph", "Current", "From name", "Source", "Action"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(240)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.show_all = QtGui.QCheckBox("Show unchanged")
        footer.addWidget(self.show_all)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Assign")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.overwrite.toggled, lambda *a: self.refresh())
        self._connect(self.show_all.toggled, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
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
        """Re-read the font and the selection (also after edits made elsewhere)."""
        self.package = current_package()
        self.selection = selected_names() if self.package else []
        index = self.scope.currentIndex if self.scope.count else (0 if len(self.selection) > 1 else 1)
        self.scope.blockSignals(True)
        self.scope.clear()
        self.scope.addItem(f"Selected glyphs ({len(self.selection)})")
        self.scope.addItem("All glyphs in the font")
        self.scope.setCurrentIndex(index)
        self.scope.blockSignals(False)
        self.refresh()

    def refresh(self):
        self.refresh_listing()
        show_rebuilds(self, [row[0] for row in self.rows if row[4] == "assign"])

    def refresh_listing(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.apply_button.setEnabled(False)
            return
        unicodes = font_unicodes()
        names = self.selection if self.scope.currentIndex == 0 else list(unicodes)
        self.rows = plan(names, unicodes, self.overwrite.isChecked())
        shown = [r for r in self.rows if r[4] != "same" or self.show_all.isChecked()]
        self.subtitle.setText(f"{len(names)} glyph{'s' if len(names) != 1 else ''} checked. Names like uni0141, "
                              "u1F600, Lslash or Wacute give a code point; suffixed names are skipped.")
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        alert = QtGui.QColor("#d33")
        self.table.setRowCount(len(shown))
        for row, (name, current, code, source, status) in enumerate(shown):
            cells = [name, hexes(current), hexes([code]), source, status]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column == 2 and status == "assign":
                    item.setForeground(QtGui.QBrush(accent))
                if column == 4 and status not in ("assign", "same"):
                    item.setForeground(QtGui.QBrush(alert))
                self.table.setItem(row, column, item)
        todo = sum(1 for r in self.rows if r[4] == "assign")
        blocked = sum(1 for r in self.rows if r[4] not in ("assign", "same"))
        same = len(self.rows) - todo - blocked
        self.apply_button.setEnabled(todo > 0)
        self.status.setText(f"{todo} to assign · {blocked} blocked · {same} already right")

    def apply(self):
        changed = run(self.package, self.rows)
        self.last_result = {"changed": changed}
        fontlab.UpdateAll()
        self.refresh()
        self.status.setText(f"Assigned {len(changed)} code point{'s' if len(changed) != 1 else ''}")

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
    dialog = UnicodeFromNames(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
