#FLM: Cleanup · Select Unreferenced Glyphs
# this_file: samples/cleanup_unused_glyphs_report.py
"""List unencoded glyphs that nothing references, and select them in the Font window for review.

A glyph counts as referenced when it has a code point, is used as a component or in an
auto recipe on any layer, is named in the OpenType feature source, or belongs to a feature
class that the source uses. Candidates are often alternates waiting for a feature, so the
script only selects them; it never deletes. Feature files pulled in with include() cannot
be read and stop the scan.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Select Unreferenced Glyphs"
KEY = "cleanup_unused_glyphs_report"
RESERVED = {".notdef", ".null", "nonmarkingreturn"}


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def font_names():
    import FL

    font = FL.fl.font
    return [font[i].name for i in range(len(font))]


def feature_source(font):
    features = font.features
    return features.get_prefix() + "\n" + "\n".join(features.get_feature(tag) for tag in features.keys())


def tokens(text):
    """Glyph and class names in FEA text (comments dropped; FEA names may contain hyphens)."""
    return set(re.findall(r"[A-Za-z0-9_.-]+", re.sub(r"#[^\n]*", "", text)))


def class_members(font, used_tokens):
    """Members of feature classes whose name the feature source uses."""
    groups = font.groups
    fea = {str(name) for name, group in groups.items() if group.isFeaGroup()}
    members = set()
    for record in groups.getAsClassRecords() or []:
        name, _, body = str(record).partition(":")
        if name in fea and name in used_tokens:
            members.update(part.rstrip("'") for part in body.split())
    return members


def unreferenced(package):
    """[(name, note)] of unencoded glyphs nothing references, in font order."""
    font = fontlab.CurrentFont()
    source = feature_source(font)
    if re.search(r"\binclude\s*\(", re.sub(r"#[^\n]*", "", source)):
        raise ValueError("The feature source uses include(): open the included code in FontLab first.")
    used = tokens(source) | RESERVED
    used |= class_members(font, used)
    names = font_names()
    glyphs = [g for g in (package.findName(n) for n in names) if g is not None]
    for glyph in glyphs:
        for layer in glyph.layers:
            used.update(shape.shapeData.componentGlyph for shape in layer.shapes if shape.isComponent)
            used.update(tokens(layer.recipe or ""))
    known = set(names)
    rows = []
    for glyph in glyphs:
        if glyph.name in used or list(glyph.fgGlyph.unicodes):
            continue
        base = glyph.name.split(".")[0]
        note = f"alternate of {base}?" if "." in glyph.name and base in known else ""
        rows.append((glyph.name, note))
    return rows


def select(names):
    """Select exactly `names` in the Font window."""
    import FL

    font = FL.fl.font
    wanted = set(names)
    for index in range(len(font)):
        FL.fl.Select(index, int(font[index].name in wanted))
    fontlab.UpdateAll()
    return {"selected": len(wanted)}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
    color.setAlpha(160)
    return color.name(QtGui.QColor.HexArgb)


class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self.setMinimumWidth(560)
        self._connections = []
        self.rows = []
        self.last_result = None
        self.package = current_package()
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        face = heading.font
        face.setPointSizeF(face.pointSizeF() * 1.35)
        face.setBold(True)
        heading.setFont(face)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel(
            "Unencoded glyphs not used as components, in auto recipes, in the feature code or in its classes. "
            "Many are alternates waiting for a feature: review before deleting anything.")
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        self.table = QtGui.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Glyph", "Hint"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(250)
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setAutoDefault(False)
        self.apply_button = QtGui.QPushButton("Select in Font window")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._safe(self.refresh)

    def _safe(self, callback):
        try:
            callback()
        except Exception as error:  # an exception escaping a PythonQt slot can take FontLab down
            self.status.setText(f"{error}")
            self.apply_button.setEnabled(False)

    def _connect(self, signal, slot):
        guarded = lambda *a: self._safe(lambda: slot(*a))
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font, then run this script again.")
            self.apply_button.setEnabled(False)
            return
        self.rows = unreferenced(self.package)
        self.table.setRowCount(len(self.rows))
        for row, cells in enumerate(self.rows):
            for column, text in enumerate(cells):
                self.table.setItem(row, column, QtGui.QTableWidgetItem(text))
        self.apply_button.setEnabled(bool(self.rows))
        count = len(self.rows)
        self.status.setText(f"{count} unreferenced glyph{'s' if count != 1 else ''}" if count
                            else "Every glyph is encoded or referenced")

    def apply(self):
        self.last_result = select([name for name, note in self.rows])
        self.status.setText(f"Selected {self.last_result['selected']} glyphs in the Font window for review")

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        windows = getattr(sys, "_fontlab_samples", {})
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
