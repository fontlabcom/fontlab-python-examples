#FLM: Masters · Interpolation Preview
# this_file: samples/masters_interpolation_preview.py
"""Preview a glyph between two masters with a slider, from the masters' own nodes.

Pick two masters and drag the slider: the painter blends every node linearly (0 % = first
master, 100 % = second) and draws the result over faint outlines of both masters. Incompatible
layers (different contour or node structure) are reported instead of drawn. Read-only.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Interpolation Preview"
KEY = "masters_interpolation_preview"


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
def outline(layer):
    """Own contours plus component contours placed by their transforms, as [(x, y, on)] lists."""
    result = []
    for shape in layer.shapes:
        transform = shape.transform
        for contour in shape.contours:
            points = node_points(contour)
            if not transform.isIdentity():
                points = [(p.x(), p.y(), on) for x, y, on in points for p in [transform.map(QtCore.QPointF(x, y))]]
            result.append(points)
    return result


def problem(a, b):
    """Why outlines a and b cannot interpolate, or None."""
    if len(a) != len(b):
        return f"{len(a)} vs {len(b)} contours"
    for i, (ca, cb) in enumerate(zip(a, b), start=1):
        if [p[2] for p in ca] != [p[2] for p in cb]:
            return f"contour {i}: {len(ca)} vs {len(cb)} nodes or different node types"
    return None


def blend(a, b, t):
    return [[(pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t, pa[2]) for pa, pb in zip(ca, cb)]
            for ca, cb in zip(a, b)]


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


class BlendView(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.report, self._paint_error = None, ""
        self.setMinimumHeight(300)
        self.a, self.b, self.mix, self.message = [], [], [], ""

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
        text = QtGui.QColor(palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
        if self.message:
            painter.setPen(text)
            painter.drawText(self.rect, int(QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap), self.message)
        path_a, path_b = outline_path(self.a), outline_path(self.b)
        rect = path_a.boundingRect().united(path_b.boundingRect())
        painter.setTransform(fit_transform(rect, self.width, self.height, 24))
        faint = QtGui.QColor(text)
        faint.setAlpha(70)
        pen = QtGui.QPen(faint)
        pen.setCosmetic(True)
        pen.setStyle(QtCore.Qt.DashLine)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush())
        painter.drawPath(path_a)
        painter.drawPath(path_b)
        if self.mix:
            accent = QtGui.QColor(palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link))  # copy: color() can alias the palette
            fill = QtGui.QColor(text)
            fill.setAlpha(200)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(fill))
            painter.drawPath(outline_path(self.mix))
            dot = QtGui.QPen(accent)
            dot.setCosmetic(True)
            dot.setWidthF(4)
            dot.setCapStyle(QtCore.Qt.RoundCap)
            painter.setPen(dot)
            for contour in self.mix:
                for x, y, on in contour:
                    if on:
                        painter.drawPoint(QtCore.QPointF(x, y))


class Interpolation(SampleDialog):
    ACTION = None

    def build(self):
        self.setMinimumWidth(560)
        grid = self.form()
        self.glyph_combo = QtGui.QComboBox()
        for name in self.names:
            self.glyph_combo.addItem(name)
        self.first, self.second = QtGui.QComboBox(), QtGui.QComboBox()
        for combo in (self.first, self.second):
            for master in self.masters:
                combo.addItem(master)
        if len(self.masters) > 1:
            self.second.setCurrentIndex(len(self.masters) - 1)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.percent = QtGui.QLabel("50 %")
        self.percent.setMinimumWidth(48)
        self.percent.setAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
        for combo in (self.glyph_combo, self.first, self.second):
            self._connect(combo.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.slider.valueChanged, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Glyph"), 0, 0)
        grid.addWidget(self.glyph_combo, 0, 1, 1, 3)
        grid.addWidget(QtGui.QLabel("Between"), 1, 0)
        grid.addWidget(self.first, 1, 1)
        grid.addWidget(QtGui.QLabel("and"), 1, 2)
        grid.addWidget(self.second, 1, 3)
        grid.addWidget(QtGui.QLabel("Position"), 2, 0)
        grid.addWidget(self.slider, 2, 1, 1, 2)
        grid.addWidget(self.percent, 2, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        self.view = BlendView()
        self.view.report = self.paint_report
        self.root.addWidget(self.view, 1)

    def refresh(self):
        if not hasattr(self, "view"):
            return
        self.mix = []
        if not self.describe_selection():
            self.view.a = self.view.b = self.view.mix = []
            self.view.update()
            return
        glyph = self.package.findName(self.glyph_combo.currentText)
        layers = master_layers(glyph, self.masters)
        first, second = layers.get(self.first.currentText), layers.get(self.second.currentText)
        t = self.slider.value / 100.0
        self.percent.setText(f"{self.slider.value} %")
        a = outline(first) if first is not None else []
        b = outline(second) if second is not None else []
        why = problem(a, b)
        self.view.a, self.view.b = a, b
        if why is None:
            self.mix = blend(a, b, t)
            self.view.message = ""
            self.status.setText(f"{glyph.name}: {self.slider.value} % from {self.first.currentText} "
                                f"to {self.second.currentText} · {sum(len(c) for c in a)} nodes")
        else:
            self.view.message = f"Not compatible: {why}"
            self.status.setText(f"{glyph.name} cannot interpolate between these masters: {why}")
        self.view.mix = self.mix
        self.view.update()


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = Interpolation(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
