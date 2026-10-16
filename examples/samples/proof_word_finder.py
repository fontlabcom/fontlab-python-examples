#FLM: Proofs · Word Finder
# this_file: samples/proof_word_finder.py
"""Find real words to proof with: words the font can set, that use the letters you are working on.

Searches a small embedded English and Latin word list. Keep only words
whose every letter has a glyph, require some letters (e.g. the new 'k'),
or restrict to a set of letters (e.g. what is drawn so far). Copy the
result as proof text. Nothing in the font changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Word Finder"
KEY = "proof_word_finder"
ENGLISH = """
about above across actually adjust after again against agree ahead album alive allow almost alone along already
always amazing amber among amount anchor ancient angle animal answer anything apart appear apple arch archive area
argue armour around arrive artist aspect assume attack audience author autumn average avoid awake aware balance
banner barely basket battle beach beauty become before begin behind believe below beside better beyond bicycle
binary bishop black blanket blend block blossom board bold border bottle bottom bounce bracket branch brave bread
breeze bridge bright bring broad bronze brother brought brush bubble budget build bundle burden butter button
cabin cactus calendar calm camera candle canvas capital captain carbon careful carpet carry castle casual catalog
cattle caught ceiling centre century chain chalk chamber change chapter charm cheap check cheese cherry chimney
choice chorus circle citizen classic clever client cliff climate clock closer cloud coast coffee collect colour
column comfort common compact complex concert copper corner cotton county couple course craft crane crisp crowd
crystal culture current curtain curve cycle daily damage dance danger dawn debate decade decide deep define degree
delicate demand design detail diamond differ dinner direct dizzy doctor dolphin double dozen draft dragon drawer
dream drift drink drive during eager early earth easily editor effort eight either elbow elegant eleven empire
empty enable energy engine enjoy enough entire equal escape essay estate evening event every exact example excuse
exhibit expect expert explain extra fabric factor fairly family famous fancy farmer fashion father favour feather
feature fellow fence fever fiction field figure final finger finish flavour flight flower fluent focus folder
follow forest forget formal format fortune forward fossil fountain fragile frame freedom frozen future galaxy
garden gather gentle giant ginger glance global glove golden grammar grape gravity grocer guitar habit hammer handle
happen harbour harvest health heavy height helmet hidden history hobby honest horizon humble hunger husband
iceberg ignore image impact indeed inside invite island jacket jaguar jazz jelly jewel jigsaw journey judge juice
jumble jungle junior justify kayak keeper kernel kettle keyboard kidney kingdom kitchen kitten knight knock knowledge
label ladder laptop large later laughter lavender layer leader leather lemon letter level liberty light limit
liquid little lizard lobster local logic lonely lumber luxury lyrics machine magnet maize making manner maple marble
market master matter meadow medium melody memory method middle minute mirror mixture modern moment monkey mountain
muffin museum music mystery napkin narrow nature nearby needle nephew nervous network neutral nobody normal notice
novel number object obtain ocean office olive onion opinion orange orbit orchard origin outfit oxygen oyster paddle
palace panther paper parade parcel parrot pattern peanut pencil people pepper perfect phrase piano picnic pillow
pilot planet plastic pocket poetry police polite powder prize problem public puzzle pyramid quality quantum quarter
queen quick quiet quilt quite quiver quote rabbit radio raven razor ready reason record region relax remote rhythm
ribbon riddle river rocket rubber rugby saddle salmon sample scarf school science season second secret seven
shadow shelter signal silver simple sketch sleepy slogan smooth snack soccer soldier sphinx spirit square squeeze
squirrel stable street string studio subject sudden summer sunset survey switch symbol system table tackle talent
temple thank theory thirty thumb ticket timber tobacco toward travel treaty trophy truly tunnel twelve twenty
typical umbrella uncle under unique update upward useful vacuum valley velvet verb victory village violin virtual
visual vivid voice volcano voyage waffle walnut wander warmth weather welcome whisky window winter wizard wonder
worry wrist writer yacht yellow yesterday yogurt young youth zebra zero zigzag zipper zombie zone
"""
LATIN = """
ab accusamus ad adipiscing aliqua aliquam aliquip amet animi anim aute beatae blanditiis commodo consectetur
consequat cupidatat culpa deserunt dicta dignissim dolor dolore dolorem duis eiusmod elit enim eos esse est
eiusmod excepteur exercitation facilis fugiat fugit harum id illum incididunt ipsa ipsum irure iusto labore
laboris laborum lorem magna minim mollit nam natus nemo neque nisi nostrud nulla obcaecati occaecat officia omnis
pariatur perferendis placeat porro proident quam quas qui quia quis quod ratione recusandae reprehenderit rerum
sapiente sed sint sit sunt tempor tempora tenetur ullamco ut velit veniam vero vitae voluptate voluptas
"""
WORDS = sorted(set(ENGLISH.split()) | set(LATIN.split()))
CASES = ["lowercase", "Capitalised", "UPPERCASE"]


# ---------------------------------------------------------------- font access
def font_chars():
    """Every character the current font encodes."""
    font = fontlab.CurrentFont()
    return {chr(code) for glyph in (font.glyphs if font is not None else []) for code in glyph.unicodes}


# ---------------------------------------------------------------- core
def cased(word, case):
    return word.upper() if case == "UPPERCASE" else word.capitalize() if case == "Capitalised" else word


def find_words(words, available, case="lowercase", must="", only="", min_len=3, max_len=12):
    """Words (in the chosen case) that the font can set and that satisfy the letter filters."""
    must = must.lower()
    only = set(only.lower())
    out = []
    for word in words:
        if not min_len <= len(word) <= max_len:
            continue
        if must and not all(letter in word for letter in must):
            continue
        if only and not set(word) <= only:
            continue
        text = cased(word, case)
        if all(char in available for char in text):
            out.append(text)
    return out


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class WordFinder(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(560)
        self.resize(600, 520)
        self._connections = []
        self.available = font_chars()
        self.words = []

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
        self.must = QtGui.QLineEdit()
        self.must.setPlaceholderText("e.g. kz")
        self.only = QtGui.QLineEdit()
        self.only.setPlaceholderText("e.g. hamburgefonstiv (empty = any)")
        self.case = QtGui.QComboBox()
        for label in CASES:
            self.case.addItem(label)
        self.min_len = QtGui.QSpinBox()
        self.min_len.setRange(1, 20)
        self.min_len.setValue(3)
        self.max_len = QtGui.QSpinBox()
        self.max_len.setRange(1, 20)
        self.max_len.setValue(12)
        lengths = QtGui.QHBoxLayout()
        lengths.addWidget(self.min_len)
        lengths.addWidget(QtGui.QLabel("to"))
        lengths.addWidget(self.max_len)
        lengths.addStretch(1)
        form.addWidget(QtGui.QLabel("Must contain"), 0, 0)
        form.addWidget(self.must, 0, 1)
        form.addWidget(QtGui.QLabel("Case"), 0, 2)
        form.addWidget(self.case, 0, 3)
        form.addWidget(QtGui.QLabel("Only letters"), 1, 0)
        form.addWidget(self.only, 1, 1)
        form.addWidget(QtGui.QLabel("Length"), 1, 2)
        form.addLayout(lengths, 1, 3)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.result_view = QtGui.QPlainTextEdit()
        self.result_view.setReadOnly(True)
        bigger = self.result_view.font
        bigger.setPointSizeF(bigger.pointSizeF() * 1.2)
        self.result_view.setFont(bigger)
        root.addWidget(self.result_view, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.copy_button = QtGui.QPushButton("Copy words")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.copy_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        for line in (self.must, self.only):
            self._connect(line.textChanged, lambda *a: self.refresh())
        for spin in (self.min_len, self.max_len):
            self._connect(spin.valueChanged, lambda *a: self.refresh())
        self._connect(self.case.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.copy_button.clicked, lambda *a: self.copy())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

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
        case = CASES[self.case.currentIndex]
        self.words = find_words(WORDS, self.available, case, self.must.text.strip(), self.only.text.strip(),
                                self.min_len.value, self.max_len.value)
        if not self.available:
            self.subtitle.setText("Open a font with encoded glyphs first.")
        else:
            self.subtitle.setText(f"{len(WORDS)} English and Latin words; showing those the font can set "
                                  f"with its {len(self.available)} characters.")
        self.result_view.setPlainText(" ".join(self.words))
        self.copy_button.setEnabled(bool(self.words))
        self.status.setText(f"{len(self.words)} word{'s' if len(self.words) != 1 else ''}")

    def copy(self):
        QtGui.QApplication.clipboard().setText(" ".join(self.words))
        self.status.setText(f"Copied {len(self.words)} words")

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
    dialog = WordFinder(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
