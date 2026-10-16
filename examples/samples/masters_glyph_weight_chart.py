#FLM: Masters · Glyph Weight Chart
# this_file: samples/masters_glyph_weight_chart.py
"""Bar chart of the ink area of the selected glyphs in every master.

Ink area is the filled area of the outline: contour areas from the flattened curves, counters
subtracted by nesting. Overlapping contours are counted twice, so remove overlaps first for exact
numbers. Each glyph gets one bar per master in axis order, labelled in thousands of square units.
Read-only.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Glyph Weight Chart"
KEY = "masters_glyph_weight_chart"
STEPS = 12
MAX_GLYPHS = 10


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


def master_layers(glyph, masters):
    """{master: flLayer} for the masters present in this glyph."""
    found = {}
    for master in masters:
        layer = glyph.findLayer(master)
        if layer is not None and not layer.isNull:
            found[master] = layer
    return found


def node_points(contour):
    return [(node.x, node.y, bool(node.isOn())) for node in contour.nodes()]


# ---------------------------------------------------------------- core
def polygon(points):
    """Flatten [(x, y, on)] of a closed contour: cubic for two handles, polyline otherwise."""
    if not points:
        return []
    start = next((i for i, p in enumerate(points) if p[2]), 0)
    pts = points[start:] + points[:start]
    poly, handles, current = [pts[0][:2]], [], pts[0][:2]
    for x, y, on in pts[1:] + pts[:1]:
        if not on:
            handles.append((x, y))
            continue
        if len(handles) == 2:
            (ax, ay), (bx, by), (cx, cy), (dx, dy) = current, handles[0], handles[1], (x, y)
            for i in range(1, STEPS + 1):
                t = i / STEPS
                u = 1 - t
                poly.append((u ** 3 * ax + 3 * u * u * t * bx + 3 * u * t * t * cx + t ** 3 * dx,
                             u ** 3 * ay + 3 * u * u * t * by + 3 * u * t * t * cy + t ** 3 * dy))
        else:
            poly.extend(handles)
            poly.append((x, y))
        current, handles = (x, y), []
    poly.extend(handles)
    return poly


def inside(point, poly):
    x, y = point
    hit = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def ink_area(contours):
    """Filled area of contours [(x, y, on)]: + for even nesting depth, - for odd (counters)."""
    polys = [polygon(points) for points in contours]
    total = 0.0
    for i, poly in enumerate(polys):
        if len(poly) < 3:
            continue
        area = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))) / 2.0
        depth = sum(1 for j, other in enumerate(polys) if j != i and len(other) > 2 and inside(poly[0], other))
        total += area if depth % 2 == 0 else -area
    return total


def layer_contours(layer):
    """Own and component contours, components placed by their transforms."""
    result = []
    for shape in layer.shapes:
        transform = shape.transform
        for contour in shape.contours:
            points = node_points(contour)
            if not transform.isIdentity():
                points = [(p.x(), p.y(), on) for x, y, on in points for p in [transform.map(QtCore.QPointF(x, y))]]
            result.append(points)
    return result


# ---------------------------------------------------------------- GUI kit
def muted(widget, alpha=150):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
    color.setAlpha(alpha)
    return color.name(QtGui.QColor.HexArgb)


def make_table(headers, min_height=280):
    table = QtGui.QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
    table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
    header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
    table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    table.setMinimumHeight(min_height)
    return table


def fill_table(table, rows, highlight=None):
    """Fill a QTableWidget; a 2-tuple row (label, note) shows the note muted across the row."""
    accent = QtGui.QColor(table.palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link))  # copy: color() can alias the palette
    ink = QtGui.QColor(table.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
    note_color = QtGui.QColor(ink)
    note_color.setAlpha(130)
    table.clearSpans()
    table.setRowCount(0)
    table.setRowCount(len(rows))
    for row, cells in enumerate(rows):
        for column, text in enumerate(cells):
            item = QtGui.QTableWidgetItem(text)
            item.setForeground(QtGui.QBrush(ink))
            if len(cells) == 2 and column == 1:
                item.setForeground(QtGui.QBrush(note_color))
                if table.columnCount > 2:
                    table.setSpan(row, 1, 1, table.columnCount - 1)
            elif column:
                item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if highlight is not None and highlight(row, column, text):
                    bold = item.font()
                    bold.setBold(True)
                    item.setFont(bold)
                    item.setForeground(QtGui.QBrush(accent))
            table.setItem(row, column, item)


class SampleDialog(QtGui.QDialog):
    """Heading, muted subtitle, the subclass's body, then a footer: status, Close, action button."""

    ACTION = "Apply"

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(520)
        # FontLab can report a light Text colour on a light Base, and its inactive group is paler
        # still (a dialog loses focus to the Font window after Apply): use the active WindowText.
        palette = self.palette
        ink = QtGui.QColor(palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
        for group in (QtGui.QPalette.Active, QtGui.QPalette.Inactive):
            for role in (QtGui.QPalette.WindowText, QtGui.QPalette.Text, QtGui.QPalette.ButtonText):
                palette.setColor(group, role, ink)
            palette.setColor(group, QtGui.QPalette.Link, palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link))
        self.setPalette(palette)
        self.package = current_package()
        self.names = selected_names() if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""
        self._connections = []
        self.last_error = ""

        self.root = QtGui.QVBoxLayout(self)
        self.root.setContentsMargins(20, 18, 20, 16)
        self.root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        self.root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        self.root.addWidget(self.subtitle)

        self.build()

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.close_button)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        if self.ACTION:
            self.apply_button = QtGui.QPushButton(self.ACTION)
            self.apply_button.setDefault(True)
            footer.addWidget(self.apply_button)
            self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self.root.addLayout(footer)
        try:
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def _connect(self, signal, slot):
        """Connect through a guard: an exception in a slot is shown in the status line, never raised into Qt."""
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:
                self.show_error(error)
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def paint_report(self, text):
        """Painters call this when drawing failed; the message stays in last_error for tests."""
        self.last_error = text
        self.status.setText(text)

    def show_error(self, error):
        self.last_error = f"{type(error).__name__}: {error}"
        status = getattr(self, "status", None)
        if status is not None:
            status.setText(f"Error: {self.last_error}")

    def scope_combo(self):
        combo = QtGui.QComboBox()
        combo.addItem(f"Current master ({self.current_master})")
        combo.addItem(f"All masters ({len(self.masters)})")
        self._connect(combo.currentIndexChanged, lambda *a: self.refresh())
        return combo

    def chosen_masters(self):
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def form(self):
        grid = QtGui.QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        self.root.addLayout(grid)
        return grid

    def describe_selection(self, what="glyph"):
        """Subtitle for the selection; False when there is nothing to work on."""
        count = len(self.names)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return False
        if not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
            return False
        shown = ", ".join(self.names[:8]) + (" …" if count > 8 else "")
        self.subtitle.setText(f"{count} {what}{'s' if count != 1 else ''}: {shown}")
        return True

    def glyphs(self):
        found = [self.package.findName(name) for name in self.names] if self.package else []
        return [glyph for glyph in found if glyph is not None]

    def build(self):
        pass

    def refresh(self):
        pass

    def apply(self):
        pass

    def closeEvent(self, event):
        self.teardown()
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        getattr(sys, "_fontlab_samples", {}).pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)

    def teardown(self):
        pass


def master_order(package):
    """Masters sorted by their location on the first axis (font order when there is no axis)."""
    masters = list(package.masters)
    axes = list(package.axes)
    if not axes:
        return masters
    key = axes[0].shortName

    def position(master):
        try:
            return float(package.location(master)[key])
        except Exception:
            return 0.0

    return sorted(masters, key=position)


def series_colors(widget, count):
    """count distinguishable colours derived from the palette accent (hue steps of the golden angle)."""
    base = QtGui.QColor(widget.palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link))  # copy: color() can alias the palette
    hue = max(base.hsvHue(), 0)
    colors = []
    for i in range(count):
        color = QtGui.QColor()
        color.setHsv(int(hue + i * 137.5) % 360, max(base.hsvSaturation(), 150), min(max(base.value(), 170), 220))
        colors.append(color)
    return colors


def nice_ticks(low, high, count=5):
    """Round tick values covering low..high."""
    import math

    span = max(high - low, 1e-9)
    raw = span / count
    magnitude = 10 ** math.floor(math.log10(raw))
    step = min((m * magnitude for m in (1, 2, 2.5, 5, 10) if m * magnitude >= raw), default=raw)
    start = math.floor(low / step) * step
    ticks, value = [], start
    while value <= high + step * 0.5:
        ticks.append(value)
        value += step
    return ticks


class BarChart(QtGui.QWidget):
    """Groups of bars: one group per glyph, one bar per master, shared y scale."""

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.report, self._paint_error = None, ""
        self.setMinimumSize(560, 300)
        self.masters, self.groups = [], []  # groups: [(glyph, [area per master])]

    def paintEvent(self, event):
        self._paint_error = ""
        painter = QtGui.QPainter(self)
        try:
            self.draw(painter)
        except Exception as error:  # an exception escaping paintEvent crashes FontLab
            self._paint_error = repr(error)
            if self.report is not None:
                self.report(f"Drawing failed: {self._paint_error}")
        finally:
            painter.end()

    def draw(self, painter):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        palette = self.palette
        painter.fillRect(self.rect, palette.color(QtGui.QPalette.Base))
        values = [v for _, row in self.groups for v in row]
        if not values:
            return
        text = QtGui.QColor(palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
        faint = QtGui.QColor(text)
        faint.setAlpha(40)
        ticks = nice_ticks(0, max(values))
        high = ticks[-1] or 1
        left, right, top, bottom = 56, self.width - 12, 34, self.height - 30
        small = QtGui.QFont(painter.font())
        small.setPointSizeF(small.pointSizeF() * 0.85)
        painter.setFont(small)
        for tick in ticks:
            y = bottom - tick / high * (bottom - top)
            painter.setPen(faint)
            painter.drawLine(QtCore.QPointF(left, y), QtCore.QPointF(right, y))
            painter.setPen(text)
            painter.drawText(QtCore.QRectF(0, y - 8, left - 8, 16), int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter),
                             f"{tick / 1000:g}k")
        colors = series_colors(self, len(self.masters))
        x = left + 4
        for i, (master, color) in enumerate(zip(self.masters, colors)):
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(color))
            painter.drawRoundedRect(QtCore.QRectF(x, 10, 10, 10), 2, 2)
            painter.setPen(text)
            painter.drawText(QtCore.QRectF(x + 14, 6, 120, 18), int(QtCore.Qt.AlignVCenter), master)
            x += 24 + painter.boundingRect(QtCore.QRectF(0, 0, 400, 20), 0, master).width()  # no QFontMetrics in PythonQt
        group = (right - left) / len(self.groups)
        bar = min(28, group * 0.8 / max(len(self.masters), 1))
        for g, (name, row) in enumerate(self.groups):
            start = left + g * group + (group - bar * len(row)) / 2
            for m, (value, color) in enumerate(zip(row, colors)):
                height = value / high * (bottom - top)
                rect = QtCore.QRectF(start + m * bar + 1, bottom - height, bar - 2, height)
                painter.setPen(QtCore.Qt.NoPen)
                painter.setBrush(QtGui.QBrush(color))
                painter.drawRoundedRect(rect, 2, 2)
            painter.setPen(text)
            painter.drawText(QtCore.QRectF(left + g * group, bottom + 6, group, 18), int(QtCore.Qt.AlignHCenter), name)


class WeightChart(SampleDialog):
    ACTION = None

    def build(self):
        self.setMinimumWidth(620)
        self.chart = BarChart()
        self.chart.report = self.paint_report
        self.root.addWidget(self.chart, 1)
        self.table = make_table(["Glyph"], 90)
        self.root.addWidget(self.table)

    def refresh(self):
        if not hasattr(self, "chart"):
            return
        self.areas = {}
        if not self.describe_selection():
            self.chart.groups = []
            self.chart.update()
            return
        order = master_order(self.package)
        for glyph in self.glyphs()[:MAX_GLYPHS]:
            found = master_layers(glyph, order)
            self.areas[glyph.name] = [ink_area(layer_contours(found[m])) if m in found else 0.0 for m in order]
        self.chart.masters = order
        self.chart.groups = list(self.areas.items())
        self.chart.update()
        self.table.setColumnCount(len(order) + 1)
        self.table.setHorizontalHeaderLabels(["Glyph"] + [f"{m} (units²)" for m in order])
        self.table.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        fill_table(self.table, [(name,) + tuple(f"{v:,.0f}" for v in row) for name, row in self.areas.items()])
        self.status.setText("Ink area per master · overlapping contours count twice")


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = WeightChart(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
