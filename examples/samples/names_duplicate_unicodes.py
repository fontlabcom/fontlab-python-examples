#FLM: Names · Duplicate Unicodes
# this_file: samples/names_duplicate_unicodes.py
"""Find code points assigned to more than one glyph and remove them from the extra glyphs.

Each shared code point is a group; ticked glyphs lose that code point on
Apply. By default the glyph that has it as its first (primary) code point
keeps it, preferring the earliest in font order. Untick to keep. One Undo
step.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Duplicate Unicodes"
KEY = "names_duplicate_unicodes"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def font_unicodes():
    """[(glyph name, [code points])] for the current font, in font order."""
    font = fontlab.CurrentFont()
    return [(g.name, list(g.unicodes)) for g in font.glyphs] if font is not None else []


# ---------------------------------------------------------------- core
def notify(package, glyphs):
    """One Undo step needs the same [layers + glyphs] list notified before and after the edit."""
    if glyphs:
        layers = [g.findLayer(package.master) or g.layers[0] for g in glyphs]
        layers = [layer for layer in layers if not layer.autoLayer]  # notifying auto layers re-resolves them all
        fontlab.flItems().notifyChangesApplied(TITLE, layers + glyphs)


def duplicates(glyphs):
    """[(code, keeper, [names])] for every code point used by more than one glyph, in code order."""
    users = {}
    for name, codes in glyphs:
        for code in codes:
            users.setdefault(code, []).append((name, codes))
    out = []
    for code in sorted(users):
        group = users[code]
        if len(group) < 2:
            continue
        primary = [name for name, codes in group if codes and codes[0] == code]
        keeper = primary[0] if primary else group[0][0]
        out.append((code, keeper, [name for name, _ in group]))
    return out


def run(package, removals):
    """Remove code points: removals = [(glyph name, code)]; one Undo step. Returns glyph names changed."""
    drop = {}
    for name, code in removals:
        glyph = package.findName(name)
        if glyph is not None and code in list(glyph.fgGlyph.unicodes):
            drop.setdefault(name, (glyph, set()))[1].add(code)
    glyphs = [glyph for glyph, _ in drop.values()]
    notify(package, glyphs)
    for glyph, codes in drop.values():
        glyph.fgGlyph.unicodes = [c for c in glyph.fgGlyph.unicodes if c not in codes]
    notify(package, glyphs)
    changed = drop
    return sorted(changed)


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


def printable(code):
    char = chr(code)
    return char if char.isprintable() and not char.isspace() else ""


class DuplicateUnicodes(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(480)
        self.resize(520, 480)
        self._connections = []
        self.groups = []

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

        self.tree = QtGui.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Code point · glyph", "Action"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        header = self.tree.header()
        header.setSectionResizeMode(0, QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        root.addWidget(self.tree, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Rescan")
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Remove ticked")
        self.apply_button.setDefault(True)
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.tree.itemChanged, lambda *a: self.update_actions())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
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
        self.package = current_package()
        glyphs = font_unicodes()
        self.groups = duplicates(glyphs)
        self.items = {}  # (name, code) -> QTreeWidgetItem
        self.tree.blockSignals(True)
        self.tree.clear()
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        for code, keeper, names in self.groups:
            top = QtGui.QTreeWidgetItem([f"U+{code:04X}  {printable(code)}   {len(names)} glyphs", ""])
            bold = top.font(0)
            bold.setBold(True)
            top.setFont(0, bold)
            self.tree.addTopLevelItem(top)
            for name in names:
                child = QtGui.QTreeWidgetItem([name, ""])
                child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
                child.setCheckState(0, QtCore.Qt.Unchecked if name == keeper else QtCore.Qt.Checked)
                top.addChild(child)
                self.items[(name, code)] = child
            top.setExpanded(True)
        self.tree.blockSignals(False)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not self.groups:
            self.subtitle.setText(f"No shared code points among {len(glyphs)} glyphs.")
        else:
            self.subtitle.setText(f"{len(self.groups)} code point{'s are' if len(self.groups) != 1 else ' is'} "
                                  "shared. Ticked glyphs lose that code point; unticked ones keep it.")
        self.accent = accent
        self.update_actions()

    def removals(self):
        return [key for key, item in self.items.items() if item.checkState(0) == QtCore.Qt.Checked]

    def update_actions(self):
        self.update_actions_listing()
        show_rebuilds(self, sorted({name for name, _ in self.removals()}))

    def update_actions_listing(self):
        self.tree.blockSignals(True)
        alert = QtGui.QColor("#d33")
        for (name, code), item in self.items.items():
            checked = item.checkState(0) == QtCore.Qt.Checked
            item.setText(1, f"remove U+{code:04X}" if checked else "keeps it")
            item.setForeground(1, QtGui.QBrush(alert if checked else self.accent))
        self.tree.blockSignals(False)
        count = len(self.removals())
        self.apply_button.setEnabled(count > 0)
        self.status.setText(f"{count} removal{'s' if count != 1 else ''} ticked")

    def apply(self):
        changed = run(self.package, self.removals())
        self.last_result = {"changed": changed}
        fontlab.UpdateAll()
        self.reload()
        self.status.setText(f"Updated {len(changed)} glyph{'s' if len(changed) != 1 else ''}")

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
    dialog = DuplicateUnicodes(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
