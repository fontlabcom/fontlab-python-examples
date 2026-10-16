#FLM: Masters · Width Chart
# this_file: samples/masters_width_chart.py
"""Line chart of the advance widths of the selected glyphs across masters.

Masters run left to right in axis order; each glyph is one line with its widths labelled, so a
master that breaks the progression stands out at once. Read-only.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Width Chart"
KEY = "masters_width_chart"
MAX_SERIES = 12


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


# ---------------------------------------------------------------- core
def widths(glyph, masters):
    """[(master, advance width or None)] in the given master order."""
    found = master_layers(glyph, masters)
    return [(m, float(found[m].advanceWidth) if m in found else None) for m in masters]


# ---------------------------------------------------------------- GUI kit
def muted(widget, alpha=150):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
    color.setAlpha(alpha)
    return color.name(QtGui.QColor.HexArgb)


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


class LineChart(QtGui.QWidget):
    """Masters on x, advance width on y, one coloured line per glyph."""

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.report, self._paint_error = None, ""
        self.setMinimumSize(520, 300)
        self.masters, self.series = [], []  # series: [(name, [width or None per master])]

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
        values = [v for _, row in self.series for v in row if v is not None]
        if not values or not self.masters:
            return
        text = QtGui.QColor(palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
        faint = QtGui.QColor(text)
        faint.setAlpha(40)
        ticks = nice_ticks(min(values), max(values))
        low, high = ticks[0], ticks[-1] if ticks[-1] > ticks[0] else ticks[0] + 1
        left, right, top, bottom = 56, self.width - 110, 18, self.height - 34
        step = (right - left) / max(len(self.masters) - 1, 1)

        def x_of(i):
            return left + i * step if len(self.masters) > 1 else (left + right) / 2

        def y_of(v):
            return bottom - (v - low) / (high - low) * (bottom - top)

        small = QtGui.QFont(painter.font())
        small.setPointSizeF(small.pointSizeF() * 0.85)
        painter.setFont(small)
        for tick in ticks:
            y = y_of(tick)
            painter.setPen(faint)
            painter.drawLine(QtCore.QPointF(left, y), QtCore.QPointF(right, y))
            painter.setPen(text)
            painter.drawText(QtCore.QRectF(0, y - 8, left - 8, 16), int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), f"{tick:g}")
        for i, master in enumerate(self.masters):
            painter.setPen(text)
            painter.drawText(QtCore.QRectF(x_of(i) - 60, bottom + 8, 120, 18), int(QtCore.Qt.AlignHCenter), master)
        colors = series_colors(self, len(self.series))
        rows = [[None if v is None else (QtCore.QPointF(x_of(i), y_of(v)), v) for i, v in enumerate(row)]
                for _, row in self.series]
        tops = {}  # (series, column) -> top of the value label, spread so labels never overlap
        for column in range(len(self.masters)):
            present = sorted((row[column][0].y(), k) for k, row in enumerate(rows) if row[column] is not None)
            for (_, k), y in zip(present, label_tops([y for y, _ in present], 16)):
                tops[k, column] = y
        ends = [(row_points[-1][0].y() - 8, k) for k, row_points in
                enumerate([[p for p in row if p is not None] for row in rows]) if row_points]
        end_tops = dict((k, y) for (_, k), y in zip(sorted(ends), spread([y for y, _ in sorted(ends)], 16)))
        label = QtGui.QFont(small)
        label.setBold(True)
        for k, ((name, _), color) in enumerate(zip(self.series, colors)):
            pen = QtGui.QPen(color)
            pen.setWidthF(2.2)
            painter.setPen(pen)
            points = [p for p in rows[k] if p is not None]
            for (a, _), (b, _) in zip(points, points[1:]):
                painter.drawLine(a, b)
            painter.setBrush(QtGui.QBrush(color))
            for column, entry in enumerate(rows[k]):
                if entry is None:
                    continue
                point, v = entry
                painter.drawEllipse(point, 3.5, 3.5)
                painter.drawText(QtCore.QRectF(point.x() - 30, tops[k, column], 60, 16), int(QtCore.Qt.AlignHCenter), f"{v:g}")
            if k in end_tops:
                painter.setFont(label)
                painter.drawText(QtCore.QRectF(right + 34, end_tops[k], 76, 16), int(QtCore.Qt.AlignVCenter), name)
                painter.setFont(small)


def label_tops(ys, height):
    """Tops of value labels for points sorted top to bottom: above the point, or below it when the
    label above would collide with the previous one, pushed further down if still crowded."""
    tops, last_point = [], None
    for y in ys:
        top = y - height - 4
        if tops and (top < tops[-1] + height or y - last_point < height + 14):
            top = max(y + 6, tops[-1] + height)
        tops.append(top)
        last_point = y
    return tops


def spread(ys, gap):
    """Sorted label positions pushed apart so neighbours are at least gap apart."""
    out = []
    for y in ys:
        out.append(y if not out else max(y, out[-1] + gap))
    return out


class WidthChart(SampleDialog):
    ACTION = None

    def build(self):
        self.setMinimumWidth(620)
        self.chart = LineChart()
        self.chart.report = self.paint_report
        self.root.addWidget(self.chart, 1)

    def refresh(self):
        if not hasattr(self, "chart"):
            return
        self.data = {}
        if not self.describe_selection():
            self.chart.series = []
            self.chart.update()
            return
        order = master_order(self.package)
        for glyph in self.glyphs()[:MAX_SERIES]:
            self.data[glyph.name] = widths(glyph, order)
        self.chart.masters = order
        self.chart.series = [(name, [w for _, w in row]) for name, row in self.data.items()]
        self.chart.update()
        extra = len(self.glyphs()) - MAX_SERIES
        note = f" · first {MAX_SERIES} glyphs shown" if extra > 0 else ""
        self.status.setText(f"Advance widths across {len(order)} masters{note}")


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = WidthChart(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
