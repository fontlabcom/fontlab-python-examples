#FLM: Hinting · Autohint Selected Layers
# this_file: samples/hints_autohint.py
"""Run FontLab's PostScript autohinter on the selected glyphs, per master.

Uses the bound flLayer.autohint(), which works from the font's own hinting settings (zones
and standard stems). The table shows each layer's hint counts before and after. TrueType
instructions are not touched; auto layers are skipped.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = 'Autohint Selected Layers'
KEY = "hints_autohint"


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


def hint_counts(layer):
    hints = [guide for guide in layer.guidelines if guide.isHint]
    vertical = sum(bool(guide.isVerticalQuarter) for guide in hints)
    return len(hints) - vertical, vertical


def run(glyphs, masters, horizontal=True, vertical=True):
    targets = master_layers(glyphs, masters)
    editable = [(g, m, layer) for g, m, layer in targets if not layer.autoLayer]
    objects = [layer for g, m, layer in editable] + list({g.name: g for g, m, layer in editable}.values())
    rows = []
    if objects:
        fontlab.flItems().notifyChangesApplied(TITLE, objects)
        try:
            for glyph, master, layer in editable:
                before = hint_counts(layer)
                success = layer.autohint()
                rows.append((glyph.name + " · " + master, *before, *hint_counts(layer), bool(success)))
        finally:
            fontlab.flItems().notifyChangesApplied(TITLE, objects)
            fontlab.UpdateAll()
    return {"rows": rows, "skipped": len(targets) - len(editable)}


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
        self.subtitle = QtGui.QLabel("Selected glyphs. Runs FontLab's PostScript autohinter with the font's zones and stems.")
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        self.warning = QtGui.QLabel(auto_base_warning(self.package, [g.name for g in self.glyphs]) if self.package else "")
        self.warning.setWordWrap(True)
        self.warning.setVisible(bool(self.warning.text))
        root.addWidget(self.warning)
        form = QtGui.QFormLayout()
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addRow("Masters", self.scope)

        root.addLayout(form)
        self.table = QtGui.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['Glyph · master', 'Horizontal hints', 'Vertical hints', 'Action'])
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
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())

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

    def chosen_masters(self):
        return self.masters if self.scope.currentIndex else [self.current_master]

    def show_rows(self, rows, enabled=True):
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, value in enumerate(cells):
                item = QtGui.QTableWidgetItem(str(value))
                if column in (1, 2):
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
        self.apply_button.setEnabled(bool(rows) and enabled)
        self.status.setText(f"{len(rows)} layer{'s' if len(rows) != 1 else ''} · {len(self.glyphs)} selected glyph{'s' if len(self.glyphs) != 1 else ''}")
        if self.package is None:
            self.subtitle.setText("Open a font, then run this script again.")
        elif not self.glyphs and True:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")

    def refresh(self):
        rows = []
        for glyph, master, layer in master_layers(self.glyphs, self.chosen_masters()):
            h, v = hint_counts(layer)
            rows.append((glyph.name + " · " + master, h, v, "auto layer, skipped" if layer.autoLayer else "ready"))
        self.show_rows(rows, True)

    def apply(self):
        self.last_result = run(self.glyphs, self.chosen_masters())
        self.show_rows([(name, f"{h0} → {h1}", f"{v0} → {v1}", "autohinted" if ok else "FontLab reported failure")
                        for name, h0, v0, h1, v1, ok in self.last_result["rows"]], False)
        self.status.setText(f"Processed {len(self.last_result['rows'])} layers · "
                            f"{self.last_result['skipped']} auto layers skipped")

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
