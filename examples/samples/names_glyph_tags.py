#FLM: Names · Glyph Tags
# this_file: samples/names_glyph_tags.py
"""View, add and remove glyph tags across the selected glyphs.

The table lists every tag used in the selection with how many selected
glyphs carry it. Type a tag (completion offers the font's tags) and Add,
or tick tags and Remove. Each Add or Remove is one Undo step.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Glyph Tags"
KEY = "names_glyph_tags"
VALID = re.compile(r"^[^\s,]{1,64}$")


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def selected_glyphs(package):
    """flGlyphs selected in the Font window, in font order; else the current glyph."""
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
    glyphs = [package.findName(name) for name in names]
    return [g for g in glyphs if g is not None]


def font_tags(package):
    """Every tag used anywhere in the current font, sorted."""
    font = fontlab.CurrentFont()
    tags = set()
    for fg in (font.glyphs if font is not None else []):
        glyph = package.findName(fg.name)
        if glyph is not None:
            tags.update(glyph.tags or [])
    return sorted(tags)


# ---------------------------------------------------------------- core
def notify(package, glyphs):
    """One Undo step needs the same [layers + glyphs] list notified before and after the edit."""
    if glyphs:
        layers = [g.findLayer(package.master) or g.layers[0] for g in glyphs]
        layers = [layer for layer in layers if not layer.autoLayer]  # notifying auto layers re-resolves them all
        fontlab.flItems().notifyChangesApplied(TITLE, layers + glyphs)


def tag_counts(glyphs):
    """[(tag, count)] over the glyphs, most used first."""
    counts = {}
    for glyph in glyphs:
        for tag in glyph.tags or []:
            counts[tag] = counts.get(tag, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def run(package, glyphs, add=(), remove=()):
    """Add and remove tags on every glyph; one Undo step. Returns names of glyphs changed."""
    plans = []
    for glyph in glyphs:
        old = list(glyph.tags or [])
        new = [t for t in old if t not in remove] + [t for t in add if t not in old]
        if new != old:
            plans.append((glyph, new))
    changed = [glyph for glyph, _ in plans]
    notify(package, changed)
    for glyph, new in plans:
        glyph.tags = new
    notify(package, changed)
    return [g.name for g in changed]


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


class GlyphTags(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(600)
        self.resize(620, 460)
        self._connections = []
        self.counts = []

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
        row.setSpacing(8)
        self.tag = QtGui.QLineEdit()
        self.tag.setPlaceholderText("tag, e.g. review, spacing, done")
        self.completer_model = QtGui.QStringListModel()
        self.completer = QtGui.QCompleter()
        self.completer.setModel(self.completer_model)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.tag.setCompleter(self.completer)
        self.add_button = QtGui.QPushButton("Add to selection")
        row.addWidget(QtGui.QLabel("Tag"))
        row.addWidget(self.tag, 1)
        row.addWidget(self.add_button)
        root.addLayout(row)

        self.table = QtGui.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Tag (tick to remove)", "Selected glyphs"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload selection")
        self.close_button = QtGui.QPushButton("Close")
        self.remove_button = QtGui.QPushButton("Remove ticked")
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.remove_button)
        root.addLayout(footer)

        self._connect(self.tag.textChanged, lambda *a: self.update_buttons())
        self._connect(self.tag.returnPressed, lambda *a: self.add_tag())
        self._connect(self.add_button.clicked, lambda *a: self.add_tag())
        self._connect(self.remove_button.clicked, lambda *a: self.remove_ticked())
        self._connect(self.table.itemChanged, lambda *a: self.update_buttons())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
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
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.completer_model.setStringList(font_tags(self.package) if self.package else [])
        self.refresh()

    def refresh(self):
        self.refresh_listing()
        show_rebuilds(self, [g.name for g in self.glyphs])

    def refresh_listing(self):
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then click Reload selection.")
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (" …" if count > 8 else "")
            self.subtitle.setText(f"{count} glyph{'s' if count != 1 else ''}: {names}")
        self.counts = tag_counts(self.glyphs)
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.counts))
        for row, (tag, used) in enumerate(self.counts):
            item = QtGui.QTableWidgetItem(tag)
            item.setFlags(int(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable))
            item.setCheckState(QtCore.Qt.Unchecked)
            share = QtGui.QTableWidgetItem(f"{used} of {count}")
            share.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
            if used == count:
                share.setForeground(QtGui.QBrush(accent))
            self.table.setItem(row, 0, item)
            self.table.setItem(row, 1, share)
        self.table.blockSignals(False)
        self.update_buttons()
        self.status.setText(f"{len(self.counts)} tag{'s' if len(self.counts) != 1 else ''} in the selection")

    def ticked(self):
        return [self.counts[row][0] for row in range(self.table.rowCount)
                if self.table.item(row, 0).checkState() == QtCore.Qt.Checked]

    def update_buttons(self):
        self.add_button.setEnabled(bool(self.glyphs) and bool(VALID.match(self.tag.text.strip())))
        self.remove_button.setEnabled(bool(self.ticked()))

    def add_tag(self):
        tag = self.tag.text.strip()
        if not self.glyphs or not VALID.match(tag):
            return
        changed = run(self.package, self.glyphs, add=[tag])
        self.last_result = {"added": tag, "changed": changed}
        self.after_edit(f"Added '{tag}' to {len(changed)} glyph{'s' if len(changed) != 1 else ''}")
        self.tag.clear()

    def remove_ticked(self):
        tags = self.ticked()
        changed = run(self.package, self.glyphs, remove=tags)
        self.last_result = {"removed": tags, "changed": changed}
        self.after_edit(f"Removed {', '.join(tags)} from {len(changed)} glyph{'s' if len(changed) != 1 else ''}")

    def after_edit(self, message):
        fontlab.UpdateAll()
        self.completer_model.setStringList(font_tags(self.package))
        self.refresh()
        self.status.setText(message)

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
    dialog = GlyphTags(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
