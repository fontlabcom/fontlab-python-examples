#FLM: Generators · Outline Effect
# this_file: samples/generate_outline_effect.py
"""Turn the selected glyphs into outlined (hollow) letters.

Every contour is replaced by a ring of the chosen line width, centred on the original
outline: Qt's path stroker draws the ring with round joins, FontGate's Remove Overlap cleans
the loops the stroker leaves inside corners. Advances are kept. Auto layers and layers
built from components are skipped and listed.
"""

import sys

import fontgate
import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Outline Effect"
KEY = "generate_outline_effect"


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
    """Why a master layer cannot be outlined, or "" when it can."""
    if layer is None or layer.isNull:
        return "no layer for this master"
    if layer.autoLayer:
        return "auto layer"
    if any(shape.isComponent for shape in layer.shapes):
        return "built from components"
    if not layer.getContours():
        return "no contours"
    return ""


# ---------------------------------------------------------------- geometry
def outline_path(layer):
    """The layer's contours as one QPainterPath, element transforms applied."""
    path = QtGui.QPainterPath()
    for shape in layer.shapes:
        for contour in shape.getContours():
            path.addPath(contour.cloneMapped(shape.transform).path())
    return path


def stroked(path, line):
    stroker = QtGui.QPainterPathStroker()
    stroker.setWidth(line)
    stroker.setJoinStyle(QtCore.Qt.RoundJoin)
    stroker.setCapStyle(QtCore.Qt.RoundCap)
    return stroker.createStroke(path)


def path_contours(path):
    """Closed flContours from a QPainterPath (MoveTo / LineTo / CurveTo + 2 CurveToData elements)."""
    groups, nodes, i = [], [], 0
    while i < path.elementCount():
        element = path.elementAt(i)
        kind = int(element.type)
        if kind == 0:  # MoveTo
            if nodes:
                groups.append(nodes)
            nodes = [fontlab.flNode(QtCore.QPointF(element.x, element.y))]
            i += 1
        elif kind == 1:  # LineTo
            nodes.append(fontlab.flNode(QtCore.QPointF(element.x, element.y)))
            i += 1
        else:  # CurveTo: this element is the first handle, the next two the second handle and the end point
            second, end = path.elementAt(i + 1), path.elementAt(i + 2)
            # FontLab: "curve" = cubic handle, "on" = on-curve; "off" would make TrueType quadratic points
            nodes.append(fontlab.flNode(QtCore.QPointF(element.x, element.y), nodeType="curve"))
            nodes.append(fontlab.flNode(QtCore.QPointF(second.x, second.y), nodeType="curve"))
            nodes.append(fontlab.flNode(QtCore.QPointF(end.x, end.y)))
            i += 3
    if nodes:
        groups.append(nodes)
    contours = []
    for group in groups:
        if len(group) > 1 and group[-1].position == group[0].position:
            first = group.pop()  # the closing point repeats the start: keep its type on the start node
            group[0] = first
        if len(group) > 2:
            contours.append(fontlab.flContour(group, closed=True))
    return contours


def ring_shape(layer, line):
    """flShape of the layer's stroked outline with the stroker's join loops removed (FontGate)."""
    shape = fontlab.flShape()
    shape.addContours(path_contours(stroked(outline_path(layer), line)), True)
    merged = fontgate.fgShape()
    shape.convertToFgShape(merged)
    merged.removeOverlap()
    return fontlab.flShape(merged)


def outline(jobs, line):
    """jobs: [(glyph, layer)]. Replace each layer's outlines by their stroked ring; one notify pair."""
    layers = [layer for _, layer in jobs]
    glyphs = []
    for glyph, _ in jobs:
        if glyph not in glyphs:
            glyphs.append(glyph)
    if not layers:
        return {"layers": 0, "contours": 0}
    prepared = [(layer, ring_shape(layer, line)) for layer in layers]
    items = layers + glyphs  # the same list before and after: one Undo step
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    for layer, shape in prepared:
        layer.removeAllShapes()
        layer.addShape(shape)
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    fontlab.UpdateAll()
    return {"layers": len(layers), "contours": sum(shape.contoursCount for _, shape in prepared)}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Preview(QtGui.QWidget):
    """Original (faint) and outlined result, current master, up to 8 glyphs."""

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
            painter.drawText(QtCore.QRectF(self.rect), int(QtCore.Qt.AlignCenter), "Nothing to outline")
            return
        line = self.owner.line.value
        top_y = max(layer.boundingBox.top() + layer.boundingBox.height() for _, layer in items) + line
        bottom_y = min(min(layer.boundingBox.top() for _, layer in items) - line, 0)
        columns = min(4, len(items))
        rows = (len(items) + columns - 1) // columns
        cell_w, cell_h = self.width / columns, self.height / rows
        scale = min((cell_h - 34) / (top_y - bottom_y), (cell_w - 16) / max(2.2 * l.advanceWidth for _, l in items))
        for index, (name, layer) in enumerate(items):
            left = (index % columns) * cell_w + 8
            top = (index // columns) * cell_h
            painter.setPen(ink)
            painter.drawText(QtCore.QRectF(left, top + 4, cell_w - 16, 16), int(QtCore.Qt.AlignLeft), name)
            source = outline_path(layer)
            result = stroked(source, line)
            painter.save()
            painter.translate(left, top + cell_h - 10 + bottom_y * scale)
            painter.scale(scale, -scale)
            painter.fillPath(source, QtGui.QBrush(faint))
            painter.translate(layer.advanceWidth * 1.15, 0)
            painter.fillPath(result, QtGui.QBrush(ink))
            painter.restore()


class OutlineEffect(QtGui.QDialog):
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
        self.line = QtGui.QSpinBox()
        self.line.setRange(2, 400)
        self.line.setSuffix(" units")
        self.line.setValue(30)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Line width"), 0, 0)
        form.addWidget(self.line, 0, 1)
        form.addWidget(QtGui.QLabel("Masters"), 0, 2)
        form.addWidget(self.scope, 0, 3)
        form.setColumnStretch(3, 1)
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

        self._connect(self.line.valueChanged, lambda *a: self.refresh())
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
            self.subtitle.setText(f"Replaces the outlines of the {count} with a ring of the line width, "
                                  "centred on the current outline.")
        ink = QtGui.QBrush(QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText)))
        self.table.setRowCount(len(self.rows))
        for row, (glyph, master, layer, problem) in enumerate(self.rows):
            action = f"{problem}, skipped" if problem else f"outline · {len(layer.getContours())} contour{'s' if len(layer.getContours()) != 1 else ''}"
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
        self.status.setText(f"{ready} layer{'s' if ready != 1 else ''} to outline · {len(self.rows) - ready} skipped")
        self.preview.update()

    def apply(self):
        self.refresh()
        jobs = [(glyph, layer) for glyph, master, layer, problem in self.rows if not problem]
        self.last_result = outline(jobs, self.line.value)
        self.refresh()
        self.status.setText(f"Outlined {self.last_result['layers']} layers "
                            f"({self.last_result['contours']} contours now)")

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
    dialog = OutlineEffect(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
