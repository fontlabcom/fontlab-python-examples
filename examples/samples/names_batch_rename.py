#FLM: Names · Batch Rename
# this_file: samples/names_batch_rename.py
"""Find and replace in glyph names (plain text or regular expression) with a live preview.

Every new name is checked before anything changes: invalid names, names that
already exist in the font and two glyphs getting the same name are refused
(FontLab would otherwise replace the existing glyph). Components that use a
renamed glyph follow it. One Apply is one Undo step.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Batch Rename"
KEY = "names_batch_rename"
VALID = re.compile(r"^(?![0-9])[A-Za-z0-9_.\-]{1,63}$")


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


def new_name(name, find, replace, regex):
    """The replaced name; raises re.error for a bad pattern."""
    if not find:
        return name
    if regex:
        return re.sub(find, replace, name)
    return name.replace(find, replace)


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


def plan(names, existing, find, replace, regex, links=((), {})):
    """[(old, new, status)] for names that change. status: "ok", or why the rename is refused."""
    rows = [(old, new_name(old, find, replace, regex)) for old in names]
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


def run(package, rows):
    """Rename every "ok" row; one Undo step. Returns [(old, new)] renamed."""
    todo = [(old, new, package.findName(old)) for old, new, status in rows if status == "ok"]
    todo = [(old, new, g) for old, new, g in todo if g is not None and package.findName(new) is None]
    glyphs = [g for _, _, g in todo]
    notify(package, glyphs)
    renamed = [(old, new) for old, new, glyph in todo if package.renameGlyph(glyph.fgGlyph, new, False)]
    notify(package, glyphs)
    return renamed


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Renamer(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(540)
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
        self.find = QtGui.QLineEdit()
        self.find.setPlaceholderText("text or pattern, e.g. ^uni or \\.alt$")
        self.replace = QtGui.QLineEdit()
        self.replace.setPlaceholderText("replacement, groups as \\1")
        self.regex = QtGui.QCheckBox("Regular expression")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Selected glyphs ({len(self.selection)})")
        self.scope.addItem("All glyphs in the font")
        form.addWidget(QtGui.QLabel("Find"), 0, 0)
        form.addWidget(self.find, 0, 1)
        form.addWidget(QtGui.QLabel("Replace"), 1, 0)
        form.addWidget(self.replace, 1, 1)
        form.addWidget(QtGui.QLabel("Glyphs"), 2, 0)
        form.addWidget(self.scope, 2, 1)
        form.addWidget(self.regex, 3, 1)
        form.setColumnStretch(1, 1)
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
        self.table.setMinimumHeight(220)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Rename")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        for line in (self.find, self.replace):
            self._connect(line.textChanged, lambda *a: self.refresh())
        self._connect(self.regex.toggled, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        if not self.selection:
            self.scope.setCurrentIndex(1)
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

    def names(self):
        return self.selection if self.scope.currentIndex == 0 else font_names()

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.apply_button.setEnabled(False)
            return
        self.subtitle.setText("Renames the glyphs and every component that uses them. "
                              "Kerning and features keep the old names; glyphs in auto-layer composites are refused "
                              "(FontLab rebuilds those from their names).")
        error = ""
        try:
            self.rows = plan(self.names(), font_names(), self.find.text, self.replace.text, self.regex.isChecked(),
                             self.links)
        except re.error as exc:
            self.rows, error = [], f"Pattern error: {exc}"
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
        if error:
            self.status.setText(error)
        elif not self.find.text:
            self.status.setText("Type the text to find.")
        else:
            note = f" · {refused} refused" if refused else ""
            self.status.setText(f"{ok} glyph{'s' if ok != 1 else ''} to rename{note}")

    def apply(self):
        renamed = run(self.package, self.rows)
        self.links = auto_links(self.package, font_names())
        self.last_result = {"renamed": renamed, "refused": [r for r in self.rows if r[2] != "ok"]}
        fontlab.UpdateAll()
        renamed_map = dict(renamed)
        self.selection = [renamed_map.get(n, n) for n in self.selection]
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
    dialog = Renamer(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
