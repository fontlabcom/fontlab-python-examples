#FLM: Utilities · Batch Glyph Notes
# this_file: samples/utility_batch_glyph_notes.py
"""Set or append a note on every selected glyph at once.

Glyph notes belong to the glyph, not to a master. Set replaces each note (an empty Set
clears them); Append adds the text on a new line. The table previews every note before
and after; only glyphs whose note changes are written.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = 'Batch Glyph Notes'
KEY = "utility_batch_glyph_notes"


def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def selected_glyphs(package, all_glyphs=False):
    import FL

    font = FL.fl.font
    names = [font[i].name for i in range(len(font))
             if all_glyphs or FL.fl.Selected(i)]
    if not names and not all_glyphs:
        glyph = fontlab.CurrentGlyph()
        names = [glyph.name] if glyph is not None else []
    return [package.findName(name) for name in names]


def master_layers(glyphs, masters):
    return [(glyph, master, layer) for glyph in glyphs for master in masters
            for layer in [glyph.findLayer(master)]
            if layer is not None and not layer.isNull]


def auto_base_warning(package, names):
    """Warning text when auto composites are built on any of `names`, else "".

    Notifying an edit of such a glyph makes FontLab rebuild every auto composite in the font
    (measured on plum: notifying O dropped ecircumflex's top anchor and component locks; Undo
    restores O but not the composites)."""
    users = {}
    font = fontlab.CurrentFont()
    wanted = set(names)
    for name in [g.name for g in font.glyphs] if font is not None else []:
        glyph = package.findName(name)
        for layer in glyph.layers if glyph is not None else []:
            if layer.autoLayer:
                for shape in layer.shapes:
                    if shape.isComponent and shape.shapeData.componentGlyph in wanted:
                        users.setdefault(shape.shapeData.componentGlyph, set()).add(name)
    if not users:
        return ""
    bases = ", ".join(sorted(users)[:4]) + ("…" if len(users) > 4 else "")
    return (f"⚠ Auto composites are built on {bases}. Applying makes FontLab rebuild every auto composite "
            "in the font, which can drop their anchors and component locks; Undo does not restore them.")


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
    color.setAlpha(160)
    return color.name(QtGui.QColor.HexArgb)


SKIPPED = "auto composite, skipped"


def is_auto(glyph):
    """Glyphs with auto layers are skipped: notifying an auto layer makes FontLab re-resolve auto layers."""
    return any(layer.autoLayer for layer in glyph.layers)


def note_text(existing, text, append):
    return existing + ("\n" if existing and text else "") + text if append else text


def run(glyphs, text, append):
    edits = [(g, note_text(g.note or "", text, append)) for g in glyphs if not is_auto(g)]
    edits = [(g, value) for g, value in edits if (g.note or "") != value]
    objects = [g for g, value in edits]
    if objects:
        fontlab.flItems().notifyChangesApplied(TITLE, objects)
        try:
            for glyph, value in edits:
                glyph.note = value
        finally:
            fontlab.flItems().notifyChangesApplied(TITLE, objects)
            fontlab.UpdateAll()
    return {"glyphs": len(edits)}


class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self.setMinimumWidth(620)
        self._connections = []
        self.last_result = None
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        face = heading.font
        face.setPointSizeF(face.pointSizeF() * 1.35)
        face.setBold(True)
        heading.setFont(face)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel('Selected glyphs. A glyph note is shared by all masters; Set with an empty note clears the notes.')
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        self.warning = QtGui.QLabel(auto_base_warning(self.package, [g.name for g in self.glyphs]) if self.package else "")
        self.warning.setWordWrap(True)
        self.warning.setVisible(bool(self.warning.text))
        root.addWidget(self.warning)
        form = QtGui.QFormLayout()
        self.mode = QtGui.QComboBox()
        self.mode.addItems(["Set (replace existing notes)", "Append on a new line"])
        self.note_input = QtGui.QPlainTextEdit()
        self.note_input.setMaximumHeight(95)
        form.addRow("Operation", self.mode)
        form.addRow("Note", self.note_input)

        root.addLayout(form)
        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['Glyph', 'Existing note', 'Resulting note'])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
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
        self.apply_button = QtGui.QPushButton('Apply')
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.note_input.textChanged, lambda *a: self.refresh())
        self._safe(self.refresh)

    def _safe(self, callback):
        try:
            callback()
        except Exception as error:
            self.status.setText(f"{type(error).__name__}: {error}")
            self.apply_button.setEnabled(False)

    def _connect(self, signal, slot):
        guarded = lambda *a: self._safe(lambda: slot(*a))
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def show_rows(self, rows, enabled=True):
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, value in enumerate(cells):
                self.table.setItem(row, column, QtGui.QTableWidgetItem(str(value).replace("\n", "  ⏎  ")))
        changing = sum(1 for name, old, new in rows if old != new and new != SKIPPED)
        self.apply_button.setEnabled(changing > 0 and enabled)
        self.status.setText(f"{changing} of {len(rows)} glyph notes change")
        if self.package is None:
            self.subtitle.setText("Open a font, then run this script again.")
        elif not self.glyphs and True:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")

    def refresh(self):
        self.show_rows([(g.name, g.note or "", SKIPPED if is_auto(g) else note_text(
            g.note or "", self.note_input.toPlainText(), self.mode.currentIndex == 1)) for g in self.glyphs])

    def apply(self):
        self.last_result = run(self.glyphs, self.note_input.toPlainText(), self.mode.currentIndex == 1)
        self.refresh()
        self.status.setText(f"Updated notes on {self.last_result['glyphs']} glyphs")

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
