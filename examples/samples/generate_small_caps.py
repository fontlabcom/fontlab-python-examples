#FLM: Generators · Small Caps from Capitals
# this_file: samples/generate_small_caps.py
"""Create small-cap glyphs (h.sc, a.sc ...) from the selected capitals, on every master.

Each new glyph gets the capital's outlines scaled by separate horizontal and vertical
factors (a larger horizontal factor keeps vertical stems relatively heavier); the advance
is scaled horizontally. Results are starting points for drawing, not finished small caps.
Existing targets, auto layers and component-built capitals are skipped and listed.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Small Caps from Capitals"
KEY = "generate_small_caps"
SUFFIX = ".sc"


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


def placed_contours(layer):
    """Contour copies with each element's transform baked in (getContours ignores it)."""
    return [contour.cloneMapped(shape.transform) for shape in layer.shapes for contour in shape.getContours()]


def source_problem(layer):
    """Why a master layer cannot be copied, or "" when it can."""
    if layer is None or layer.isNull:
        return "missing master layer"
    if layer.autoLayer:
        return "auto layer"
    if any(shape.isComponent for shape in layer.shapes):
        return "built from components"
    if not layer.getContours():
        return "no contours"
    return ""


def target_name(name):
    """H -> h.sc, H.ss01 -> h.sc.ss01 (lowercase base, the usual smcp/c2sc naming)."""
    base, dot, rest = name.partition(".")
    return base.lower() + SUFFIX + (dot + rest if dot else "")


def is_capital(name):
    base = name.partition(".")[0]
    return base[:1].isupper() and base.lower() != base


# ---------------------------------------------------------------- generation
def scaled(layer, sx, sy):
    """([flContour], advance) of the layer scaled about the origin."""
    transform = QtGui.QTransform(sx, 0, 0, sy, 0, 0)
    return [c.cloneMapped(transform) for c in placed_contours(layer)], round(layer.advanceWidth * sx)


def create(package, plan, sx, sy):
    """plan: [(source glyph, target name, [(master, layer)])]. Adds glyphs, then their master layers."""
    made, touched = [], []
    for source, target, layers in plan:
        glyph = fontlab.flGlyph()
        glyph.name = target
        package.addGlyph(glyph)
        glyph = package.findName(target)  # layers exist only on the registered glyph
        for master, layer in layers:
            contours, advance = scaled(layer, sx, sy)
            new = glyph.findLayerCreate(master)
            shape = fontlab.flShape()
            shape.addContours(contours, True)
            new.addShape(shape)
            new.advanceWidth = advance
            touched.append(new)
        made.append(glyph)
    if made:
        fontlab.flItems().notifyChangesApplied(TITLE, touched + made)
        fontlab.UpdateAll()
    return {"glyphs": len(made), "layers": len(touched)}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def contours_path(contours):
    path = QtGui.QPainterPath()
    for contour in contours:
        path.addPath(contour.path())
    return path


class Preview(QtGui.QWidget):
    """Capital (faint) and its small cap (solid) side by side, current master, up to 8 glyphs."""

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
            painter.drawText(QtCore.QRectF(self.rect), int(QtCore.Qt.AlignCenter), "Nothing to create")
            return
        sx, sy = self.owner.factors()
        upm = max(max(layer.boundingBox.top() + layer.boundingBox.height(), 1) for _, layer in items)
        columns = min(4, len(items))
        rows = (len(items) + columns - 1) // columns
        cell_w, cell_h = self.width / columns, self.height / rows
        scale = min((cell_h - 34) / upm, (cell_w - 16) / max(2.1 * layer.advanceWidth for _, layer in items))
        for index, (target, layer) in enumerate(items):
            left = (index % columns) * cell_w + 8
            top = (index // columns) * cell_h
            painter.setPen(ink)
            painter.drawText(QtCore.QRectF(left, top + 4, cell_w - 16, 16), int(QtCore.Qt.AlignLeft), target)
            source = contours_path(placed_contours(layer))
            result, _ = scaled(layer, sx, sy)
            painter.save()
            painter.translate(left, top + cell_h - 10)
            painter.scale(scale, -scale)
            painter.fillPath(source, QtGui.QBrush(faint))
            painter.translate(layer.advanceWidth * 1.08, 0)
            painter.fillPath(contours_path(result), QtGui.QBrush(ink))
            painter.restore()


class SmallCaps(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(620)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self._connections = []
        self.plan = []
        self.last_result = None
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []

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

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        self.x_scale = QtGui.QSpinBox()
        self.y_scale = QtGui.QSpinBox()
        for spin, value in ((self.x_scale, 75), (self.y_scale, 70)):
            spin.setRange(10, 200)
            spin.setSuffix(" %")
            spin.setValue(value)
        form.addWidget(QtGui.QLabel("Horizontal scale"), 0, 0)
        form.addWidget(self.x_scale, 0, 1)
        form.addWidget(QtGui.QLabel("Vertical scale"), 0, 2)
        form.addWidget(self.y_scale, 0, 3)
        form.setColumnStretch(4, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["New glyph", "From", "Action"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(130)
        root.addWidget(self.table, 1)
        self.preview = Preview(self)
        root.addWidget(self.preview, 2)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setAutoDefault(False)
        self.apply_button = QtGui.QPushButton("Create")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.x_scale.valueChanged, lambda *a: self.refresh())
        self._connect(self.y_scale.valueChanged, lambda *a: self.refresh())
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

    def factors(self):
        return self.x_scale.value / 100, self.y_scale.value / 100

    def build_plan(self):
        """[(glyph, target, [(master, layer)], problem)] for the selected capitals."""
        rows = []
        for glyph in self.glyphs:
            if not is_capital(glyph.name):
                continue
            target = target_name(glyph.name)
            layers = [(m, glyph.findLayer(m)) for m in self.masters]
            problems = sorted({p for p in (source_problem(layer) for _, layer in layers) if p})
            if self.package.findName(target) is not None:
                problems = ["exists"]
            rows.append((glyph, target, layers, ", ".join(problems)))
        return rows

    def preview_items(self):
        master = self.package.master if self.package else ""
        return [(target, dict(layers)[master]) for glyph, target, layers, problem in self.plan if not problem]

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.plan = []
        else:
            self.plan = self.build_plan()
            if not self.plan:
                self.subtitle.setText("Select capitals in the Font window, then run this script again.")
            else:
                self.subtitle.setText(
                    f"Creates a scaled small cap for each selected capital on all {len(self.masters)} masters. "
                    "Existing glyphs are never overwritten.")
        ink = QtGui.QBrush(QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText)))
        self.table.setRowCount(len(self.plan))
        for row, (glyph, target, layers, problem) in enumerate(self.plan):
            action = f"{problem}, skipped" if problem else f"create · {len(layers)} masters"
            for column, text in enumerate((target, glyph.name, action)):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(ink)
                self.table.setItem(row, column, item)
        ready = sum(1 for row in self.plan if not row[3])
        self.apply_button.setEnabled(ready > 0)
        self.status.setText(f"{ready} glyph{'s' if ready != 1 else ''} to create · {len(self.plan) - ready} skipped")
        self.preview.update()

    def apply(self):
        self.refresh()
        sx, sy = self.factors()
        ready = [(glyph, target, layers) for glyph, target, layers, problem in self.plan if not problem]
        self.last_result = create(self.package, ready, sx, sy)
        self.refresh()
        self.status.setText(f"Created {self.last_result['glyphs']} glyphs ({self.last_result['layers']} master layers)")

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
    dialog = SmallCaps(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
