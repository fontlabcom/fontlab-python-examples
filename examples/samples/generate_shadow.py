#FLM: Generators · Shadow Copy
# this_file: samples/generate_shadow.py
"""Add a shifted copy of the selected glyphs' outlines as a separate shadow element.

The copy goes behind the original as its own element, so it can be recoloured, moved or
deleted as a unit, or split into a layer font's shadow glyphs. Original and shadow overlap;
filled as one glyph they merge into an extruded silhouette. Advances are kept. Auto layers
and layers built from components are skipped.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Shadow Copy"
KEY = "generate_shadow"
SHADOW = "shadow"  # element name of the added copy


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


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


def auto_bases(package):
    """{glyph name: [auto composites built on it]} over the whole font.

    Notifying an edit of such a glyph makes FontLab rebuild every auto composite in the font
    (measured on plum: notifying O dropped ecircumflex's top anchor and component locks; Undo
    restores O but not the composites), so the dialog warns before Apply."""
    font = fontlab.CurrentFont()
    bases = {}
    for name in [g.name for g in font.glyphs] if font is not None else []:
        glyph = package.findName(name)
        for layer in glyph.layers if glyph is not None else []:
            if layer.autoLayer:
                for shape in layer.shapes:
                    if shape.isComponent:
                        bases.setdefault(shape.shapeData.componentGlyph, set()).add(name)
    return {base: sorted(users) for base, users in bases.items()}


def layer_problem(layer):
    """Why a master layer cannot get a shadow, or "" when it can."""
    if layer is None or layer.isNull:
        return "no layer for this master"
    if layer.autoLayer:
        return "auto layer"
    if any(shape.isComponent for shape in layer.shapes):
        return "built from components"
    if not layer.getContours():
        return "no contours"
    if any(shape.name == SHADOW for shape in layer.shapes):
        return "has a shadow already"
    return ""


# ---------------------------------------------------------------- geometry
def shifted_contours(layer, dx, dy):
    """Copies of the layer's contours, element transforms applied, moved by (dx, dy)."""
    move = QtGui.QTransform(1, 0, 0, 1, dx, dy)
    return [contour.cloneMapped(shape.transform).cloneMapped(move)
            for shape in layer.shapes for contour in shape.getContours()]


def contours_path(contours):
    path = QtGui.QPainterPath()
    for contour in contours:
        path.addPath(contour.path())
    return path


def add_shadows(jobs, dx, dy):
    """jobs: [(glyph, layer)]. Insert a shadow element first in each layer; one notify pair."""
    layers = [layer for _, layer in jobs]
    glyphs = []
    for glyph, _ in jobs:
        if glyph not in glyphs:
            glyphs.append(glyph)
    if not layers:
        return {"layers": 0}
    prepared = [(layer, shifted_contours(layer, dx, dy)) for layer in layers]
    items = layers + glyphs  # the same list before and after: one Undo step
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    for layer, contours in prepared:
        shape = fontlab.flShape()
        shape.addContours(contours, True)
        shape.name = SHADOW
        layer.insertShape(0, shape)
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    fontlab.UpdateAll()
    return {"layers": len(layers)}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Preview(QtGui.QWidget):
    """Glyph (ink) over its shadow (faint), current master, up to 8 glyphs."""

    def __init__(self, owner):
        QtGui.QWidget.__init__(self, owner)
        self.owner = owner
        self.paint_error = ""
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        self.paint_error = ""
        painter = QtGui.QPainter(self)
        try:
            self.draw(painter)
        except Exception as error:  # an exception escaping paintEvent can take FontLab down
            self.paint_error = repr(error)
            self.owner.status.setText(f"Preview failed: {error}")
        finally:
            painter.end()

    def draw(self, painter):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        palette = self.palette
        painter.fillRect(self.rect, palette.color(QtGui.QPalette.Base))
        ink = QtGui.QColor(palette.color(QtGui.QPalette.WindowText))
        faint = QtGui.QColor(ink)
        faint.setAlpha(55)
        items = self.owner.preview_items()[:8]
        if not items:
            painter.setPen(ink)
            painter.drawText(QtCore.QRectF(self.rect), int(QtCore.Qt.AlignCenter), "Nothing to shadow")
            return
        dx, dy = self.owner.dx.value, self.owner.dy.value
        top_y = max(layer.boundingBox.top() + layer.boundingBox.height() for _, layer in items) + max(dy, 0)
        bottom_y = min(min(layer.boundingBox.top() for _, layer in items) + min(dy, 0), 0)
        columns = min(4, len(items))
        rows = (len(items) + columns - 1) // columns
        cell_w, cell_h = self.width / columns, self.height / rows
        scale = min((cell_h - 34) / (top_y - bottom_y), (cell_w - 16) / max(l.advanceWidth + abs(dx) + 40 for _, l in items))
        for index, (name, layer) in enumerate(items):
            left = (index % columns) * cell_w + 8
            top = (index // columns) * cell_h
            painter.setPen(ink)
            painter.drawText(QtCore.QRectF(left, top + 4, cell_w - 16, 16), int(QtCore.Qt.AlignLeft), name)
            painter.save()
            painter.translate(left + max(-dx, 0) * scale, top + cell_h - 10 + bottom_y * scale)
            painter.scale(scale, -scale)
            painter.fillPath(contours_path(shifted_contours(layer, dx, dy)), QtGui.QBrush(faint))
            painter.fillPath(contours_path(shifted_contours(layer, 0, 0)), QtGui.QBrush(ink))
            painter.restore()


class ShadowCopy(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(600)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self._connections = []
        self.rows = []
        self.last_result = None
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self.bases = auto_bases(self.package) if self.package else {}

        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        face = heading.font
        face.setPointSizeF(face.pointSizeF() * 1.35)
        face.setBold(True)
        heading.setFont(face)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        self.warning = QtGui.QLabel()
        self.warning.setWordWrap(True)
        root.addWidget(self.warning)

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        self.dx = QtGui.QSpinBox()
        self.dy = QtGui.QSpinBox()
        for spin, value in ((self.dx, 40), (self.dy, -40)):
            spin.setRange(-500, 500)
            spin.setSuffix(" units")
            spin.setValue(value)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Shift right"), 0, 0)
        form.addWidget(self.dx, 0, 1)
        form.addWidget(QtGui.QLabel("Shift up"), 0, 2)
        form.addWidget(self.dy, 0, 3)
        form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        form.addWidget(self.scope, 1, 1, 1, 3)
        form.setColumnStretch(4, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Glyph · master", "Action"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(120)
        root.addWidget(self.table, 1)
        self.preview = Preview(self)
        root.addWidget(self.preview, 2)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setAutoDefault(False)
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.dx.valueChanged, lambda *a: self.refresh())
        self._connect(self.dy.valueChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal, slot):
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:  # an exception escaping a PythonQt slot can take FontLab down
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def chosen_masters(self):
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def preview_items(self):
        return [(glyph.name, layer) for glyph, master, layer, problem in self.rows
                if not problem and master == self.current_master]

    def refresh(self):
        self.rows = [(glyph, master, glyph.findLayer(master), layer_problem(glyph.findLayer(master)))
                     for glyph in self.glyphs for master in self.chosen_masters()]
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not self.glyphs:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
        else:
            count = f"{len(self.glyphs)} selected glyph{'s' if len(self.glyphs) != 1 else ''}"
            self.subtitle.setText(f"Adds a shifted copy of the outlines of the {count} behind them, "
                                  f"as one element named \"{SHADOW}\".")
        ink = QtGui.QBrush(QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText)))
        self.table.setRowCount(len(self.rows))
        for row, (glyph, master, layer, problem) in enumerate(self.rows):
            action = f"{problem}, skipped" if problem else f"add shadow · {len(layer.getContours())} contour{'s' if len(layer.getContours()) != 1 else ''}"
            for column, text in enumerate((f"{glyph.name} · {master}", action)):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(ink)
                self.table.setItem(row, column, item)
        ready = sum(1 for row in self.rows if not row[3])
        bases = sorted({glyph.name for glyph, master, layer, problem in self.rows if not problem and glyph.name in self.bases})
        self.warning.setText(
            f"⚠ Auto composites are built on {', '.join(bases[:4])}{'…' if len(bases) > 4 else ''}. Applying makes "
            "FontLab rebuild every auto composite in the font, which can drop their anchors and component locks; "
            "Undo does not restore them." if bases else "")
        self.warning.setVisible(bool(bases))
        self.apply_button.setEnabled(ready > 0)
        self.status.setText(f"{ready} layer{'s' if ready != 1 else ''} to shadow · {len(self.rows) - ready} skipped")
        self.preview.update()

    def apply(self):
        self.refresh()
        jobs = [(glyph, layer) for glyph, master, layer, problem in self.rows if not problem]
        self.last_result = add_shadows(jobs, self.dx.value, self.dy.value)
        self.refresh()
        self.status.setText(f"Added a shadow to {self.last_result['layers']} layers")

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
    dialog = ShadowCopy(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
