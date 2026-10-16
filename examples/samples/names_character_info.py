#FLM: Names · Character Info
# this_file: samples/names_character_info.py
"""A live panel describing the character of the glyph selected in the Font window.

Shows the outline next to the system font's rendering, the code point, the
Unicode name and category (Python's unicodedata), case counterpart,
decomposition and the UTF-8/UTF-16 encodings. It follows the selection
twice a second; nothing in the font changes.
"""

import sys
import unicodedata

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Character Info"
KEY = "names_character_info"
POLL_MS = 500
CATEGORIES = {
    "Lu": "Letter, uppercase", "Ll": "Letter, lowercase", "Lt": "Letter, titlecase", "Lm": "Letter, modifier",
    "Lo": "Letter, other", "Mn": "Mark, nonspacing", "Mc": "Mark, spacing", "Me": "Mark, enclosing",
    "Nd": "Number, decimal", "Nl": "Number, letter", "No": "Number, other", "Pc": "Punctuation, connector",
    "Pd": "Punctuation, dash", "Ps": "Punctuation, open", "Pe": "Punctuation, close", "Pi": "Punctuation, initial",
    "Pf": "Punctuation, final", "Po": "Punctuation, other", "Sm": "Symbol, math", "Sc": "Symbol, currency",
    "Sk": "Symbol, modifier", "So": "Symbol, other", "Zs": "Separator, space", "Cc": "Control", "Cf": "Format",
    "Co": "Private use", "Cn": "Unassigned",
}
FIELDS = ["Glyph", "Code point", "Unicode name", "Category", "Case pair", "Decomposition", "UTF-8", "UTF-16", "Escape"]


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def focused_name():
    """First glyph selected in the Font window, else the current glyph; None without a font."""
    try:
        import FL

        font = FL.fl.font
        for i in range(len(font)):
            if FL.fl.Selected(i):
                return font[i].name
    except Exception:
        pass
    glyph = fontlab.CurrentGlyph()
    return glyph.name if glyph is not None else None


def layer_path(layer):
    """The layer's outline as one QPainterPath in font units (y up), components placed."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        for part in (shape.closedPath, shape.openedPath):
            if part is not None and not part.isEmpty():
                path.addPath(shape.transform.map(part))
    return path


# ---------------------------------------------------------------- core
def describe(code):
    """{field: text} for one code point (pure Python, no font access)."""
    char = chr(code)
    category = unicodedata.category(char)
    upper, lower = char.upper(), char.lower()
    pair = lower if char != lower else upper if char != upper else ""
    utf16 = char.encode("utf-16-be")
    return {
        "Code point": f"U+{code:04X}",
        "Unicode name": unicodedata.name(char, "(no name)"),
        "Category": f"{category} · {CATEGORIES.get(category, '')}",
        "Case pair": " ".join(f"{c} U+{ord(c):04X}" for c in pair) if pair else "–",
        "Decomposition": unicodedata.decomposition(char) or "–",
        "UTF-8": " ".join(f"{b:02X}" for b in char.encode("utf-8")),
        "UTF-16": " ".join(utf16[i:i + 2].hex().upper() for i in range(0, len(utf16), 2)),
        "Escape": f"\\u{code:04x}" if code <= 0xFFFF else f"\\U{code:08x}",
    }


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Specimen(QtGui.QWidget):
    """Custom painter: the glyph outline (left) and the system font's character (right)."""

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.paint_error = ""
        self.on_error = None  # dialog hook: show drawing errors in the status label
        self.setMinimumHeight(150)
        self.path, self.advance, self.char = None, 0, ""
        self.frame = (-250, 750)

    def set_content(self, path, advance, char, frame):
        self.path, self.advance, self.char, self.frame = path, advance, char, frame
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        try:
            self.draw(painter)
            self.paint_error = ""
        except Exception as error:  # an escaping exception with a live QPainter crashes FontLab
            self.paint_error = repr(error)
            if self.on_error is not None:
                self.on_error(self.paint_error)
        finally:
            painter.end()

    def draw(self, painter):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        text = QtGui.QColor(self.palette.color(QtGui.QPalette.Text))
        faint = QtGui.QColor(text)
        faint.setAlpha(35)
        soft = QtGui.QColor(text)
        soft.setAlpha(120)
        half = self.width / 2.0
        height = self.height
        painter.setPen(QtGui.QPen(QtGui.QBrush(faint), 1.0))
        painter.drawRoundedRect(QtCore.QRectF(0.5, 0.5, half - 6, height - 1), 8, 8)
        painter.drawRoundedRect(QtCore.QRectF(half + 6, 0.5, half - 6.5, height - 1), 8, 8)
        small = QtGui.QFont(painter.font())
        small.setPointSizeF(max(8.0, small.pointSizeF() * 0.85))
        painter.setFont(small)
        painter.setPen(soft)
        painter.drawText(QtCore.QRectF(8, height - 22, half - 20, 18), int(QtCore.Qt.AlignLeft), "Font outline")
        painter.drawText(QtCore.QRectF(half + 14, height - 22, half - 20, 18), int(QtCore.Qt.AlignLeft), "System font")
        descender, ascender = self.frame
        if self.path is not None:
            scale = (height - 34) / float(max(1.0, ascender - descender))
            baseline = 8 + ascender * scale
            painter.setPen(QtGui.QPen(QtGui.QBrush(faint), 1.0))
            painter.drawLine(QtCore.QPointF(8, baseline), QtCore.QPointF(half - 14, baseline))
            painter.save()
            painter.translate((half - 6 - self.advance * scale) / 2.0, baseline)
            painter.scale(scale, 0 - scale)
            painter.fillPath(self.path, QtGui.QBrush(text))
            painter.restore()
        if self.char:
            big = QtGui.QFont(painter.font())
            big.setPixelSize(int(height * 0.55))
            painter.setFont(big)
            painter.setPen(text)
            painter.drawText(QtCore.QRectF(half + 6, 0, half - 6, height - 18), int(QtCore.Qt.AlignCenter), self.char)


class CharacterInfo(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(480)
        self._connections = []
        self.shown_name = None

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

        self.specimen = Specimen()
        root.addWidget(self.specimen)

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(6)
        self.fields = {}
        for row, label in enumerate(FIELDS):
            caption = QtGui.QLabel(label)
            caption.setStyleSheet(f"color: {muted(self)};")
            value = QtGui.QLabel("–")
            value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            value.setWordWrap(True)
            caption.setAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop))
            form.addWidget(caption, row, 0)
            form.addWidget(value, row, 1)
            self.fields[label] = value
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.others = QtGui.QLabel()
        self.others.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.others)
        root.addStretch(1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.specimen.on_error = lambda text: self.status.setText("Drawing failed: " + text)
        self.copy_button = QtGui.QPushButton("Copy character")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.copy_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(POLL_MS)
        self._connect(self.timer.timeout, lambda *a: self.poll())
        self._connect(self.copy_button.clicked, lambda *a: self.copy())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()
        self.timer.start()

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

    def poll(self):
        if focused_name() != self.shown_name:
            self.refresh()

    def refresh(self, name=None):
        package = current_package()
        name = name or (focused_name() if package else None)
        self.shown_name = name
        glyph = package.findName(name) if package and name else None
        self.current = {}
        if glyph is None:
            self.subtitle.setText("Open a font and select a glyph in the Font window." if package is None
                                  else "Select a glyph in the Font window.")
            for value in self.fields.values():
                value.setText("–")
            self.specimen.set_content(None, 0, "", (-250, 750))
            self.copy_button.setEnabled(False)
            return
        codes = list(glyph.fgGlyph.unicodes)
        layer = glyph.findLayer(package.master)
        path = layer_path(layer) if layer is not None else None
        char = chr(codes[0]) if codes else ""
        frame = (package.descender_value, package.ascender_value)
        self.specimen.set_content(path, layer.advanceWidth if layer is not None else 0, char, frame)
        self.subtitle.setText(f"Follows the Font window selection · master {package.master}")
        self.current = describe(codes[0]) if codes else {}
        self.current["Glyph"] = name
        for label, value in self.fields.items():
            value.setText(self.current.get(label, "– (unencoded)" if label == "Code point" else "–"))
        self.others.setText("Also encoded: " + ", ".join(f"U+{c:04X}" for c in codes[1:]) if len(codes) > 1 else "")
        self.copy_button.setEnabled(bool(char))
        self.status.setText(f"{name} · {len(codes)} code point{'s' if len(codes) != 1 else ''}")

    def copy(self):
        if self.specimen.char:
            QtGui.QApplication.clipboard().setText(self.specimen.char)
            self.status.setText(f"Copied {self.specimen.char}")

    def closeEvent(self, event):
        self.timer.stop()
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
    dialog = CharacterInfo(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
