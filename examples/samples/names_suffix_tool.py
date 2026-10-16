#FLM: Names · Suffix Tool
# this_file: samples/names_suffix_tool.py
"""Add, remove or replace a glyph-name suffix (.ss01, .sc, .alt…) on the selected glyphs.

The preview shows every new name and refuses names that already exist or
collide, so no glyph is ever replaced. Suffixed alternates are usually not
encoded: optionally move their Unicode off. Components follow the rename.
One Apply is one Undo step.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Suffix Tool"
KEY = "names_suffix_tool"
PRESETS = [".ss01", ".ss02", ".sc", ".alt", ".case", ".sups", ".lf", ".osf", ".tf", ".001"]
VALID = re.compile(r"^(?![0-9])[A-Za-z0-9_.\-]{1,63}$")
MODES = [("Add suffix", "add"), ("Remove suffix", "remove"), ("Replace suffix", "replace")]


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


def font_names():
    font = fontlab.CurrentFont()
    return [g.name for g in font.glyphs] if font is not None else []


# ---------------------------------------------------------------- core
def notify(package, glyphs):
    """One Undo step needs the same [layers + glyphs] list notified before and after the edit."""
    if glyphs:
        layers = [g.findLayer(package.master) or g.layers[0] for g in glyphs]
        layers = [layer for layer in layers if not layer.autoLayer]  # notifying auto layers re-resolves them all
        fontlab.flItems().notifyChangesApplied(TITLE, layers + glyphs)


def text_of(combo):
    """An editable QComboBox's text (PythonQt exposes currentText as a property)."""
    value = combo.currentText
    return value() if callable(value) else value


def dotted(suffix):
    suffix = suffix.strip()
    return suffix if not suffix or suffix.startswith(".") else "." + suffix


def suffixed(name, mode, suffix, replacement=""):
    """The new name for one glyph; the name itself when the operation does not apply."""
    suffix, replacement = dotted(suffix), dotted(replacement)
    if mode == "add":
        return name + suffix if suffix and not name.endswith(suffix) else name
    base, dot, last = name[1:].rpartition(".")
    if not dot:
        return name
    current = "." + last
    stem = name[0] + base
    if mode == "remove":
        return stem if not suffix or current == suffix else name
    return stem + replacement if current == suffix and replacement else name


def auto_links(package, names):
    """(glyphs that have an auto layer, {base: [auto composites using it]}).

    FontLab rebuilds auto layers from their recipe whenever they are notified (measured: renaming e
    then notifying turned ecircumflex into a lone ee), so both sides of an auto composite are refused.
    """
    autos, bases = set(), {}
    for name in names:
        glyph = package.findName(name)
        if glyph is None:
            continue
        for layer in glyph.layers:
            if not layer.autoLayer:
                continue
            autos.add(name)
            for shape in layer.shapes:
                data = shape.shapeData
                base = data.componentGlyph if data is not None else ""
                if base:
                    bases.setdefault(base, set()).add(name)
    return autos, {base: sorted(users) for base, users in bases.items()}


def auto_refusal(name, links):
    """Why an auto-layer link refuses renaming `name`, or ""."""
    autos, bases = links
    if name in autos:
        return "has auto layers"
    users = bases.get(name)
    if users:
        return "base of auto " + ", ".join(users[:2]) + ("…" if len(users) > 2 else "")
    return ""


def plan(names, existing, mode, suffix, replacement="", links=((), {})):
    """[(old, new, status)] for names that change; status "ok" or why the rename is refused."""
    rows = [(old, suffixed(old, mode, suffix, replacement)) for old in names]
    rows = [(old, new) for old, new in rows if new != old]
    targets = {}
    for _, new in rows:
        targets[new] = targets.get(new, 0) + 1
    taken = set(existing)
    out = []
    for old, new in rows:
        if not VALID.match(new):
            status = "invalid name"
        elif auto_refusal(old, links):
            status = auto_refusal(old, links)
        elif new in taken:
            status = "exists in font"
        elif targets[new] > 1:
            status = "duplicate target"
        else:
            status = "ok"
        out.append((old, new, status))
    return out


def run(package, rows, clear_unicode):
    """Rename the "ok" rows (optionally removing their Unicode); one Undo step. Returns [(old, new)]."""
    todo = [(old, new, package.findName(old)) for old, new, status in rows if status == "ok"]
    todo = [(old, new, g) for old, new, g in todo if g is not None and package.findName(new) is None]
    glyphs = [g for _, _, g in todo]
    notify(package, glyphs)
    renamed = []
    for old, new, glyph in todo:
        if package.renameGlyph(glyph.fgGlyph, new, False):
            if clear_unicode:
                glyph.fgGlyph.unicodes = []
            renamed.append((old, new))
    notify(package, glyphs)
    return renamed


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class SuffixTool(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(520)
        self._connections = []
        self.package = current_package()
        self.selection = selected_names() if self.package else []
        self.rows = []
        self.links = auto_links(self.package, font_names()) if self.package else ((), {})

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
        self.mode = QtGui.QComboBox()
        for label, _ in MODES:
            self.mode.addItem(label)
        self.suffix = QtGui.QComboBox()
        self.suffix.setEditable(True)
        for preset in PRESETS:
            self.suffix.addItem(preset)
        self.replacement = QtGui.QComboBox()
        self.replacement.setEditable(True)
        for preset in PRESETS:
            self.replacement.addItem(preset)
        self.replacement_label = QtGui.QLabel("With")
        self.clear_unicode = QtGui.QCheckBox("Remove Unicode from renamed glyphs (alternates are unencoded)")
        self.clear_unicode.setChecked(True)
        form.addWidget(QtGui.QLabel("Operation"), 0, 0)
        form.addWidget(self.mode, 0, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Suffix"), 1, 0)
        form.addWidget(self.suffix, 1, 1)
        form.addWidget(self.replacement_label, 1, 2)
        form.addWidget(self.replacement, 1, 3)
        form.addWidget(self.clear_unicode, 2, 1, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Glyph", "New name", "Check"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(200)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.mode.currentIndexChanged, lambda *a: self.mode_changed())
        for combo in (self.suffix, self.replacement):
            self._connect(combo.editTextChanged, lambda *a: self.refresh())
        self._connect(self.clear_unicode.toggled, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.mode_changed()

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

    def mode_key(self):
        return MODES[self.mode.currentIndex][1]

    def mode_changed(self):
        replace = self.mode_key() == "replace"
        self.replacement.setVisible(replace)
        self.replacement_label.setVisible(replace)
        self.clear_unicode.setVisible(self.mode_key() != "remove")
        self.refresh()

    def refresh(self):
        count = len(self.selection)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
        else:
            names = ", ".join(self.selection[:8]) + (" …" if count > 8 else "")
            self.subtitle.setText(f"{count} glyph{'s' if count != 1 else ''}: {names}. "
                                  "Components follow; kerning and features keep the old names.")
        self.rows = plan(self.selection, font_names(), self.mode_key(), text_of(self.suffix),
                         text_of(self.replacement), self.links) if self.package else []
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        alert = QtGui.QColor("#d33")
        self.table.setRowCount(len(self.rows))
        for row, (old, new, status) in enumerate(self.rows):
            cells = [old, new, "✓" if status == "ok" else status]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column == 1 and status == "ok":
                    item.setForeground(QtGui.QBrush(accent))
                if column == 2:
                    item.setForeground(QtGui.QBrush(accent if status == "ok" else alert))
                self.table.setItem(row, column, item)
        ok = sum(1 for r in self.rows if r[2] == "ok")
        refused = len(self.rows) - ok
        self.apply_button.setEnabled(ok > 0)
        untouched = count - len(self.rows)
        parts = [f"{ok} to rename"] + ([f"{refused} refused"] if refused else []) + \
                ([f"{untouched} not affected"] if untouched else [])
        self.status.setText(" · ".join(parts))

    def apply(self):
        clear = self.clear_unicode.isChecked() and self.mode_key() != "remove"
        renamed = run(self.package, self.rows, clear)
        self.links = auto_links(self.package, font_names())
        self.last_result = {"renamed": renamed, "cleared_unicode": clear}
        fontlab.UpdateAll()
        mapping = dict(renamed)
        self.selection = [mapping.get(n, n) for n in self.selection]
        self.refresh()
        self.status.setText(f"Renamed {len(renamed)} glyph{'s' if len(renamed) != 1 else ''}")

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
    dialog = SuffixTool(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
