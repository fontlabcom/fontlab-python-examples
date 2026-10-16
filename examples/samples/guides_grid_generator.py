#FLM: Guides · Grid Generator
# this_file: samples/guides_grid_generator.py
"""Add a regular grid of named glyph guides: N lines every S units from an origin.

The painter previews the grid over the first selected glyph. Guides that already
exist (same name and position) are not added twice. Auto layers are skipped.
One Apply is one Undo step.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Grid Generator"
KEY = "guides_grid_generator"
DIRECTIONS = ["Horizontal and vertical", "Horizontal", "Vertical"]


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


def master_layers(glyph, masters):
    """[(master, flLayer)] for the masters present in this glyph."""
    found = []
    for master in masters:
        layer = glyph.findLayer(master)
        if layer is not None and not layer.isNull:
            found.append((master, layer))
    return found


def layer_path(layer):
    """The layer's outline as one QPainterPath in font units (y up), components placed."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        for part in (shape.closedPath, shape.openedPath):
            if part is not None and not part.isEmpty():
                path.addPath(shape.transform.map(part))
    return path


def grid(direction, origin, step, count):
    """Guide records (x, y, angle, name) of the grid; pure, no font access."""
    records = []
    for i in range(count):
        position = float(origin + i * step)
        if direction in (0, 1):
            records.append((0.0, position, 0.0, f"Grid H {i + 1}"))
        if direction in (0, 2):
            records.append((position, 0.0, 90.0, f"Grid V {i + 1}"))
    return records


# ---------------------------------------------------------------- guides
# flGuideLine(QLineF, flags, style): the (angle, point) overload ignores the angle in PythonQt and
# makes free "vector" guides; FontLab's own glyph guides carry these flags (flsnapline.h).
HORIZONTAL, VERTICAL, VECTOR = 0x2000, 0x4000, 0x1000  # flSnaps::Horizontal / Vertical / Vector
GLYPH_GUIDE = 0x102  # SnapObjectsStyle gsGlyphGuideline


def guide_record(guide):
    """(x, y, angle in degrees, name) of an flGuideLine; x is 0 for horizontal, y for vertical guides."""
    point = guide.centerPoint
    angle = round(math.degrees(guide.angle), 2) % 180  # flGuideLine.angle is in radians
    x, y = round(point.x(), 2), round(point.y(), 2)
    return (0.0 if angle == 0 else x, 0.0 if angle == 90 else y, angle, str(guide.name or ""))


def glyph_guides(layer):
    return [g for g in layer.guidelines if not g.isHint]


def new_guide(values):
    """A glyph guide through (x, y) at `angle` degrees (0 horizontal, 90 vertical)."""
    x, y, angle, name = values
    if angle == 0:
        line, flags = QtCore.QLineF(x, y, x + 100, y), HORIZONTAL
    elif angle == 90:
        line, flags = QtCore.QLineF(x, y, x, y + 100), VERTICAL
    else:
        radians = math.radians(angle)
        line, flags = QtCore.QLineF(x, y, x + 100 * math.cos(radians), y + 100 * math.sin(radians)), VECTOR
    guide = fontlab.flGuideLine(line, flags, GLYPH_GUIDE)
    guide.name = name
    return guide


def add_guides(jobs):
    """jobs: [(glyph, layer, [records to add])]. Notify before and after: one Undo step."""
    layers = [layer for _, layer, values in jobs if values]
    glyphs = []
    for glyph, _, values in jobs:
        if values and glyph not in glyphs:
            glyphs.append(glyph)
    if not layers:
        return {"layers": 0, "guides": 0}
    items = layers + glyphs
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    count = 0
    for _, layer, values in jobs:
        if values:
            layer.appendGuidelines([new_guide(v) for v in values])
            count += len(values)
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    fontlab.UpdateAll()
    return {"layers": len(layers), "guides": count}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class GridPreview(QtGui.QWidget):
    """Custom painter: the first glyph's outline with the planned grid lines on top."""

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setMinimumHeight(200)
        self.paint_error = ""
        self.on_error = None  # dialog hook: show drawing errors in the status label
        self.path, self.advance, self.records, self.frame = None, 0, [], (-250.0, 750.0)

    def set_content(self, path, advance, records, frame):
        self.path, self.advance, self.records, self.frame = path, advance, records, frame
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        try:
            self.draw(painter)
            self.paint_error = ""
        except Exception as error:  # an escaping exception with a live QPainter crashes FontLab
            self.paint_error = repr(error)
            if self.on_error is not None:
                self.on_error(self.paint_error)
        finally:
            painter.end()

    def draw(self, painter):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        ink = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        faint = QtGui.QColor(ink)
        faint.setAlpha(40)
        glyph_ink = QtGui.QColor(ink)
        glyph_ink.setAlpha(170)
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        width, height = float(self.width), float(self.height)
        painter.setPen(QtGui.QPen(QtGui.QBrush(faint), 1.0))
        painter.drawRoundedRect(QtCore.QRectF(0.5, 0.5, width - 1, height - 1), 8, 8)
        # frame in font units: the glyph box plus every grid position
        bottom, top = self.frame
        left, right = 0.0, float(max(self.advance, 1))
        for x, y, angle, _ in self.records:
            if angle == 0:
                bottom, top = min(bottom, y), max(top, y)
            else:
                left, right = min(left, x), max(right, x)
        scale = min((width - 40) / max(1.0, right - left), (height - 30) / max(1.0, top - bottom))
        ox = (width - (right - left) * scale) / 2.0 - left * scale
        oy = 15 + top * scale

        def to_view(x, y):
            return QtCore.QPointF(ox + x * scale, oy - y * scale)

        painter.setPen(QtGui.QPen(QtGui.QBrush(faint), 1.0))
        painter.drawLine(to_view(left, 0), to_view(right, 0))
        if self.path is not None:
            painter.save()
            painter.translate(ox, oy)
            painter.scale(scale, 0 - scale)
            painter.fillPath(self.path, QtGui.QBrush(glyph_ink))
            painter.restore()
        painter.setPen(QtGui.QPen(QtGui.QBrush(accent), 1.0))
        for x, y, angle, _ in self.records:
            if angle == 0:
                painter.drawLine(QtCore.QPointF(8, oy - y * scale), QtCore.QPointF(width - 8, oy - y * scale))
            else:
                painter.drawLine(QtCore.QPointF(ox + x * scale, 8), QtCore.QPointF(ox + x * scale, height - 8))


class GridGenerator(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(540)
        palette = self.palette
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % palette.color(QtGui.QPalette.WindowText).name())
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
        self.direction = QtGui.QComboBox()
        self.direction.addItems(DIRECTIONS)
        self.origin = self._spin(-5000, 5000, 0)
        self.step = self._spin(1, 5000, 100)
        self.count = self._spin(1, 100, 5)
        self.count.setSuffix("")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Lines"), 0, 0)
        form.addWidget(self.direction, 0, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Origin"), 1, 0)
        form.addWidget(self.origin, 1, 1)
        form.addWidget(QtGui.QLabel("Step"), 1, 2)
        form.addWidget(self.step, 1, 3)
        form.addWidget(QtGui.QLabel("Count"), 2, 0)
        form.addWidget(self.count, 2, 1)
        form.addWidget(QtGui.QLabel("Masters"), 3, 0)
        form.addWidget(self.scope, 3, 1, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        root.addLayout(form)

        self.preview = GridPreview()
        self.preview.on_error = lambda message: self.status.setText(f"Preview error: {message}")
        root.addWidget(self.preview, 1)

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Glyph · master", "Guides to add", "Already there"])
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
        root.addWidget(self.table)

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

        self._connect(self.direction.currentIndexChanged, lambda *a: self.refresh())
        for spin in (self.origin, self.step, self.count):
            self._connect(spin.valueChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _spin(self, low, high, value):
        spin = QtGui.QSpinBox()
        spin.setRange(low, high)
        spin.setValue(value)
        spin.setSuffix(" units")
        spin.setAlignment(QtCore.Qt.AlignRight)
        return spin

    def _connect(self, signal, slot):
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:  # an exception escaping a PythonQt slot can take FontLab down
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    # state
    def chosen_masters(self):
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def records(self):
        return grid(self.direction.currentIndex, self.origin.value, self.step.value, self.count.value)

    def plan(self):
        """[(glyph, master, layer, [records to add], [records already there])]."""
        wanted = self.records()
        planned = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()):
                existing = {guide_record(g) for g in glyph_guides(layer)}
                planned.append((glyph, master, layer, [r for r in wanted if r not in existing],
                                [r for r in wanted if r in existing]))
        return planned

    def refresh(self):
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (" …" if count > 8 else "")
            self.subtitle.setText(f"Adds grid guides to {count} glyph{'s' if count != 1 else ''}: {names}")
        records = self.records()
        if self.glyphs:
            layer = self.glyphs[0].findLayer(self.current_master)
            metrics = fontlab.FontMetrics(self.package, self.current_master)
            frame = (float(metrics.descender), float(metrics.ascender))
            if layer is not None and not layer.isNull:
                self.preview.set_content(layer_path(layer), layer.advanceWidth, records, frame)
        else:
            self.preview.set_content(None, 0, records, (-250.0, 750.0))
        rows = []
        for glyph, master, layer, add, there in (self.plan() if self.glyphs else []):
            if layer.autoLayer:
                rows.append((f"{glyph.name} · {master}", "auto layer, skipped", ""))
            else:
                rows.append((f"{glyph.name} · {master}", str(len(add)), str(len(there))))
        ink = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(QtGui.QBrush(ink))
                if column and text.isdigit():
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
        adds = sum(int(cells[1]) for cells in rows if cells[1].isdigit())
        self.apply_button.setEnabled(adds > 0)
        self.status.setText(f"{len(records)} grid lines · {adds} guide{'s' if adds != 1 else ''} to add")

    def apply(self):
        jobs = [(glyph, layer, add) for glyph, master, layer, add, there in self.plan() if not layer.autoLayer]
        self.last_result = add_guides(jobs)
        self.refresh()
        self.status.setText(f"Added {self.last_result['guides']} guides to {self.last_result['layers']} layers")

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
    dialog = GridGenerator(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
