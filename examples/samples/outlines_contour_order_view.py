#FLM: Outlines · Contour Order View
# this_file: samples/outlines_contour_order_view.py
"""Show every master of a glyph side by side with numbered contours, start points and directions.

Each contour carries its index at the start node, a dot on the start node and an arrow along
its first segment, so start-point and order mismatches between masters are visible at a glance
before interpolation surprises you. Read-only: nothing in the font changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Contour Order View"
KEY = "outlines_contour_order_view"


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


def own_contours(layer):
    """Contours drawn in this layer; layer.getContours() also lists the contours of components."""
    return [contour for shape in layer.shapes if not shape.isComponent for contour in shape.contours]


def node_points(contour):
    return [(node.x, node.y, bool(node.isOn())) for node in contour.nodes()]


# ---------------------------------------------------------------- core
def signed_area(points):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1])) / 2.0


def contour_info(layer):
    """[(index, points, start (x, y), next point (x, y), 'ccw'|'cw')] for the layer's own contours."""
    info = []
    for index, contour in enumerate(own_contours(layer)):
        points = node_points(contour)
        if not points:
            continue
        direction = "ccw" if signed_area([p[:2] for p in points]) > 0 else "cw"
        info.append((index, points, points[0][:2], points[1 % len(points)][:2], direction))
    return info


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


def outline_path(contours):
    """QPainterPath from contours given as [(x, y, on)] lists (cubic for two handles)."""
    path = QtGui.QPainterPath()
    for points in contours:
        start = next((i for i, p in enumerate(points) if p[2]), None)
        if start is None:
            continue
        pts = points[start:] + points[:start]
        path.moveTo(pts[0][0], pts[0][1])
        handles = []
        for x, y, on in pts[1:] + pts[:1]:
            if not on:
                handles.append((x, y))
                continue
            if len(handles) == 2:
                path.cubicTo(handles[0][0], handles[0][1], handles[1][0], handles[1][1], x, y)
            elif len(handles) == 1:
                path.quadTo(handles[0][0], handles[0][1], x, y)
            else:
                path.lineTo(x, y)
            handles = []
        path.closeSubpath()
    return path


def fit_transform(rect, width, height, margin=16):
    """QTransform mapping font units in rect (y up) into a width × height widget (y down)."""
    if rect.width() <= 0 or rect.height() <= 0:
        return QtGui.QTransform()
    scale = min((width - 2 * margin) / rect.width(), (height - 2 * margin) / rect.height())
    if scale <= 0:
        return QtGui.QTransform()
    dx = (width - rect.width() * scale) / 2 - rect.x() * scale
    dy = (height + rect.height() * scale) / 2 + rect.y() * scale
    return QtGui.QTransform(scale, 0, 0, -scale, dx, dy)


class OrderView(QtGui.QWidget):
    """One column per master: filled outline, numbered start dots and first-segment arrows."""

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.report, self._paint_error = None, ""
        self.setMinimumSize(560, 300)
        self.columns = []  # [(master, info)]

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
        if not self.columns:
            return
        text_color = QtGui.QColor(palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
        accent = QtGui.QColor(palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link))  # copy: color() can alias the palette
        union = QtCore.QRectF()
        for _, info in self.columns:
            union = union.united(outline_path([c[1] for c in info]).boundingRect())
        width = self.width / len(self.columns)
        label_font = QtGui.QFont(painter.font())
        label_font.setBold(True)
        for column, (master, info) in enumerate(self.columns):
            left = column * width
            painter.resetTransform()
            painter.setPen(text_color)
            painter.setFont(label_font)
            painter.drawText(QtCore.QRectF(left, 6, width, 20), int(QtCore.Qt.AlignHCenter), master)
            fit = fit_transform(union, width, self.height - 28, 26)
            fit = QtGui.QTransform(fit.m11(), fit.m12(), fit.m21(), fit.m22(), fit.dx() + left, fit.dy() + 28)
            ink = QtGui.QColor(text_color)
            ink.setAlpha(38)
            path = fit.map(outline_path([c[1] for c in info]))
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(ink))
            painter.drawPath(path)
            outline = QtGui.QPen(text_color)
            outline.setWidthF(1.0)
            painter.setPen(outline)
            painter.setBrush(QtGui.QBrush())
            painter.drawPath(path)
            for index, points, start, nxt, direction in info:
                p = fit.map(QtCore.QPointF(start[0], start[1]))
                q = fit.map(QtCore.QPointF(nxt[0], nxt[1]))
                self.arrow(painter, p, q, accent)
                painter.setPen(QtCore.Qt.NoPen)
                painter.setBrush(QtGui.QBrush(accent))
                painter.drawEllipse(p, 4.5, 4.5)
                painter.setPen(accent)
                painter.setFont(label_font)
                painter.drawText(QtCore.QRectF(p.x() + 6, p.y() - 20, 40, 18), 0, str(index + 1))
            if column:
                divider = QtGui.QColor(text_color)
                divider.setAlpha(40)
                painter.setPen(divider)
                painter.drawLine(QtCore.QPointF(left, 8), QtCore.QPointF(left, self.height - 8))

    def arrow(self, painter, p, q, color):
        dx, dy = q.x() - p.x(), q.y() - p.y()
        length = (dx * dx + dy * dy) ** 0.5
        if length < 1:
            return
        ux, uy = dx / length, dy / length
        tip = QtCore.QPointF(p.x() + ux * 22, p.y() + uy * 22)
        pen = QtGui.QPen(color)
        pen.setWidthF(2.0)
        painter.setPen(pen)
        painter.drawLine(p, tip)
        head = QtGui.QPolygonF()
        head.append(tip)
        head.append(QtCore.QPointF(tip.x() - ux * 8 - uy * 5, tip.y() - uy * 8 + ux * 5))
        head.append(QtCore.QPointF(tip.x() - ux * 8 + uy * 5, tip.y() - uy * 8 - ux * 5))
        painter.setBrush(QtGui.QBrush(color))
        painter.drawPolygon(head)


class ContourOrder(SampleDialog):
    ACTION = None

    def build(self):
        self.setMinimumWidth(640)
        grid = self.form()
        self.glyph_combo = QtGui.QComboBox()
        for name in self.names:
            self.glyph_combo.addItem(name)
        self._connect(self.glyph_combo.currentIndexChanged, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Glyph"), 0, 0)
        grid.addWidget(self.glyph_combo, 0, 1)
        grid.setColumnStretch(1, 1)
        self.view = OrderView()
        self.view.report = self.paint_report
        self.root.addWidget(self.view, 1)
        legend = QtGui.QLabel("● start node · number = contour order · arrow = direction of the first segment")
        legend.setStyleSheet(f"color: {muted(self)};")
        self.root.addWidget(legend)

    def refresh(self):
        self.info = {}
        if not self.describe_selection():
            self.view.columns = []
            self.view.update()
            return
        glyph = self.package.findName(self.glyph_combo.currentText)
        columns = []
        for master, layer in master_layers(glyph, self.masters).items():
            info = [] if layer.autoLayer else contour_info(layer)
            self.info[master] = [(i, start, direction, len(points)) for i, points, start, _, direction in info]
            columns.append((master + (" (auto)" if layer.autoLayer else ""), info))
        self.view.columns = columns
        self.view.update()
        counts = {len(v) for v in self.info.values()}
        note = "contour counts match" if len(counts) == 1 else "contour counts differ between masters"
        self.status.setText(f"{glyph.name}: {len(columns)} masters · {note}")


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = ContourOrder(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
