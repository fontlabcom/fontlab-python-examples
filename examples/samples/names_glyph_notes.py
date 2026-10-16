#FLM: Names · Glyph Notes
# this_file: samples/names_glyph_notes.py
"""Read and edit the note of the selected glyph, and browse every glyph that has a note.

The editor shows the note of the first glyph selected in the Font window;
Save writes it (one Undo step). The list below collects all notes in the
font; click one to edit it, double-click to also select that glyph.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Glyph Notes"
KEY = "names_glyph_notes"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def focused_name():
    """First glyph selected in the Font window, else the current glyph."""
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


def select_in_font_window(name):
    import FL

    font = FL.fl.font
    FL.fl.Unselect()
    for i in range(len(font)):
        if font[i].name == name:
            FL.fl.Select(i)
    fontlab.UpdateAll()


# ---------------------------------------------------------------- core
def notify(package, glyphs):
    """One Undo step needs the same [layers + glyphs] list notified before and after the edit."""
    if glyphs:
        layers = [g.findLayer(package.master) or g.layers[0] for g in glyphs]
        layers = [layer for layer in layers if not layer.autoLayer]  # notifying auto layers re-resolves them all
        fontlab.flItems().notifyChangesApplied(TITLE, layers + glyphs)


def notes(package):
    """[(glyph name, note)] for every glyph with a non-empty note, in font order."""
    font = fontlab.CurrentFont()
    out = []
    for fg in (font.glyphs if font is not None else []):
        glyph = package.findName(fg.name)
        text = (glyph.note or "") if glyph is not None else ""
        if text.strip():
            out.append((fg.name, text))
    return out


def run(package, name, text):
    """Set one glyph's note; one Undo step. Returns True when it changed."""
    glyph = package.findName(name)
    if glyph is None or (glyph.note or "") == text:
        return False
    notify(package, [glyph])
    glyph.note = text
    notify(package, [glyph])
    return True


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


class GlyphNotes(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(480)
        self.resize(500, 540)
        self._connections = []
        self.package = current_package()
        self.glyph_name = focused_name() if self.package else None
        self.entries = []

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

        self.editor_label = QtGui.QLabel()
        bold = self.editor_label.font
        bold.setBold(True)
        self.editor_label.setFont(bold)
        root.addWidget(self.editor_label)
        self.editor = QtGui.QPlainTextEdit()
        self.editor.setPlaceholderText("Write a note for this glyph…")
        self.editor.setMinimumHeight(110)
        root.addWidget(self.editor)

        self.list_label = QtGui.QLabel()
        self.list_label.setFont(bold)
        root.addWidget(self.list_label)
        self.list = QtGui.QTableWidget(0, 2)
        self.list.setHorizontalHeaderLabels(["Glyph", "Note"])
        self.list.verticalHeader().setVisible(False)
        self.list.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.list.setAlternatingRowColors(True)
        self.list.setShowGrid(False)
        header = self.list.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.list, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Save note")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.editor.textChanged, lambda *a: self.edited())
        self._connect(self.list.cellClicked, lambda row, *a: self.load_row(row))
        self._connect(self.list.cellDoubleClicked, lambda row, *a: self.load_row(row, select=True))
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.load(self.glyph_name)
        self.reload_list()

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

    def stored(self):
        glyph = self.package.findName(self.glyph_name) if self.package and self.glyph_name else None
        return (glyph.note or "") if glyph is not None else ""

    def load(self, name):
        self.glyph_name = name
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            self.subtitle.setText("Notes travel with the glyph in .vfc/.vfj files. Select a glyph in the Font "
                                  "window, or pick one below.")
        self.editor_label.setText(f"Note for {name}" if name else "No glyph selected")
        self.editor.setEnabled(bool(name))
        self.editor.setPlainText(self.stored())
        self.edited()

    def load_row(self, row, select=False):
        if 0 <= row < len(self.entries):
            self.load(self.entries[row][0])
            if select:
                select_in_font_window(self.entries[row][0])

    def reload_list(self):
        self.entries = notes(self.package) if self.package else []
        self.list_label.setText(f"Glyphs with notes ({len(self.entries)})")
        self.list.setRowCount(len(self.entries))
        for row, (name, text) in enumerate(self.entries):
            first = text.strip().splitlines()[0]
            for column, value in enumerate((name, first)):
                item = QtGui.QTableWidgetItem(value)
                item.setToolTip(text)
                self.list.setItem(row, column, item)

    def edited(self):
        self.edited_listing()
        show_rebuilds(self, [self.glyph_name] if self.glyph_name else [])

    def edited_listing(self):
        dirty = bool(self.glyph_name) and self.editor.toPlainText() != self.stored()
        self.apply_button.setEnabled(dirty)
        self.status.setText("Unsaved changes" if dirty else "")

    def apply(self):
        changed = run(self.package, self.glyph_name, self.editor.toPlainText())
        self.last_result = {"glyph": self.glyph_name, "changed": changed}
        fontlab.UpdateAll()
        self.reload_list()
        self.edited()
        self.status.setText(f"Saved note for {self.glyph_name}" if changed else "No change")

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
    dialog = GlyphNotes(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
