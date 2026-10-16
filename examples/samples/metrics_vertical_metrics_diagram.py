#FLM: Metrics · Vertical Metrics Diagram
# this_file: samples/metrics_vertical_metrics_diagram.py
"""See and edit ascender, cap height, x-height and descender of every master in one diagram.

Each master is drawn as a column with H, x, b and p from its own outlines against its metric
lines, so a cap height that misses the H or an x-height that cuts the x shows at a glance.
Edit the numbers in the grid; changed values are highlighted and drawn in the accent colour.
Apply writes all changed masters as one Undo step and returns to the master you were on.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Vertical Metrics"
KEY = "metrics_vertical_metrics_diagram"
FIELDS = [("Ascender", "ascender"), ("Cap height", "capsHeight"), ("x-height", "xHeight"), ("Descender", "descender")]
SAMPLE = ["H", "x", "b", "p"]
LABEL_GAP = 16  # px between line names in the margin


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def read_metrics(package):
    """{master: {field: value}}; visits each master and returns to the current one."""
    start, out = package.master, {}
    try:
        for master in list(package.masters):
            package.setMaster(master)
            out[master] = {key: round(getattr(package, key + "_value")) for _, key in FIELDS}
    finally:
        package.setMaster(start)
    return out


def outline(layer):
    """The layer's outline as one QPainterPath, components placed by their transforms."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        part = QtGui.QPainterPath()
        for contour in shape.getContours():
            part.addPath(contour.path())
        path.addPath(shape.transform.map(part))
    return path


# ---------------------------------------------------------------- core
def changes(original, edited):
    """{master: {field: new}} for the values that differ."""
    out = {}
    for master, values in edited.items():
        diff = {k: v for k, v in values.items() if original[master][k] != v}
        if diff:
            out[master] = diff
    return out


def run(package, todo):
    """Write {master: {field: value}} as one Undo step; the current master is restored."""
    if not todo:
        return {"masters": 0, "values": 0}
    items = [package, package.mastersContainer()]
    start = package.master
    package.checkInitHistoryState(0)
    fontlab.flItems.notifyChangesApplied(TITLE, items)
    try:
        for master, values in todo.items():
            package.setMaster(master)
            for key, value in values.items():
                setattr(package, key + "_value", value)
    finally:
        package.setMaster(start)
    fontlab.flItems.notifyChangesApplied(TITLE, items)
    return {"masters": len(todo), "values": sum(len(v) for v in todo.values())}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Diagram(QtGui.QWidget):
    """One column per master: sample glyphs plus labelled metric lines."""

    def __init__(self, owner):
        QtGui.QWidget.__init__(self)
        self.paint_error = None
        self.owner = owner
        self.setMinimumSize(560, 260)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        try:
            self.draw(painter)
            self.paint_error = None
        except Exception as error:  # an escaping error here can crash FontLab
            self.paint_error = repr(error)
        finally:
            painter.end()

    def draw(self, painter):
        owner = self.owner
        palette = self.palette
        painter.fillRect(self.rect, palette.color(QtGui.QPalette.Base))
        masters = owner.masters
        if not masters:
            painter.setPen(QtGui.QColor(muted(self)))
            painter.drawText(self.rect, int(QtCore.Qt.AlignCenter), "Open a font first.")
            return
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        values = owner.edited
        top = max(max(v.values()) for v in values.values()) + 60
        bottom = min(min(v.values()) for v in values.values()) - 40
        label_w, head = 84, 22
        column = (self.width - label_w - 16) / len(masters)
        scale = min((self.height - head - 12) / (top - bottom), column / max(owner.sample_width, 1) * 0.9)
        offset = head + max(self.height - head - 12 - (top - bottom) * scale, 0) / 2
        ink = QtGui.QColor(palette.color(QtGui.QPalette.WindowText))
        guide = QtGui.QColor(palette.color(QtGui.QPalette.Mid))
        accent = QtGui.QColor(palette.color(QtGui.QPalette.Link))
        dim = QtGui.QColor(muted(self))
        small = painter.font()
        small.setPointSizeF(max(small.pointSizeF() * 0.85, 8))
        painter.setFont(small)
        for i, master in enumerate(masters):
            x0 = label_w + i * column
            baseline = offset + top * scale
            painter.setPen(ink)
            painter.drawText(QtCore.QRectF(x0, 0, column, head), int(QtCore.Qt.AlignCenter), master)
            lines = [("Baseline", 0, False)] + [(label, values[master][key], owner.original[master][key] != values[master][key])
                                                for label, key in FIELDS]
            for label, y, changed in lines:
                yy = baseline - y * scale
                painter.setPen(QtGui.QPen(QtGui.QBrush(accent if changed else guide), 2.0 if changed else 1.0))
                painter.drawLine(QtCore.QPointF(x0 + 6, yy), QtCore.QPointF(x0 + column - 6, yy))
            if i == 0:
                self.draw_labels(painter, [(baseline - y * scale, label) for label, y, _ in lines], label_w, dim)
            pen_x = x0 + (column - owner.sample_width * scale) / 2
            for name, path, advance in owner.samples.get(master, []):
                painter.save()
                painter.translate(pen_x, baseline)
                painter.scale(scale, -scale)
                painter.setPen(QtCore.Qt.NoPen)
                painter.setBrush(QtGui.QBrush(ink))
                painter.drawPath(path)
                painter.restore()
                pen_x += advance * scale


    @staticmethod
    def draw_labels(painter, labels, width, color):
        """Line names right-aligned in the margin, pushed apart so close lines stay readable."""
        painter.setPen(color)
        last = None
        for yy, label in sorted(labels):
            if last is not None and yy < last + LABEL_GAP:
                yy = last + LABEL_GAP
            painter.drawText(QtCore.QRectF(0, yy - 9, width - 6, 18),
                             int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), label)
            last = yy


class VerticalMetrics(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        # The palette copy does not reach spin box text or item-view item text: style them directly.
        ink = palette.color(QtGui.QPalette.WindowText).name()
        self.setStyleSheet(f"QAbstractSpinBox, QAbstractItemView {{ color: {ink}; }}")
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(640)
        self.package = current_package()
        self.masters = list(self.package.masters) if self.package else []
        self.original = read_metrics(self.package) if self.package else {}
        self.edited = {m: dict(v) for m, v in self.original.items()}
        self.samples, self.sample_width = self.load_samples()
        self.spins = {}
        self._connections = []

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

        self.diagram = Diagram(self)
        root.addWidget(self.diagram, 1)

        grid = QtGui.QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)
        for column, (label, _) in enumerate(FIELDS, 1):
            title = QtGui.QLabel(label)
            title.setStyleSheet(f"color: {muted(self)};")
            grid.addWidget(title, 0, column)
        for row, master in enumerate(self.masters, 1):
            grid.addWidget(QtGui.QLabel(master), row, 0)
            for column, (_, key) in enumerate(FIELDS, 1):
                spin = QtGui.QSpinBox()
                spin.setRange(-4000, 4000)
                spin.setAlignment(QtCore.Qt.AlignRight)
                spin.setValue(self.original[master][key])
                self.spins[(master, key)] = spin
                grid.addWidget(spin, row, column)
                self._connect(spin.valueChanged, lambda *a, m=master, k=key: self.edit(m, k))
        for column in range(1, len(FIELDS) + 1):
            grid.setColumnStretch(column, 1)
        root.addLayout(grid)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.revert_button = QtGui.QPushButton("Revert")
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.revert_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.revert_button.clicked, lambda *a: self.revert())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal, slot):
        def guarded(*args):
            # An exception escaping a PythonQt slot can take FontLab down: report it instead.
            try:
                return slot(*args)
            except Exception as error:
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def load_samples(self):
        """{master: [(name, path, advance)]} for H x b p, and the widest sample line."""
        samples, widest = {}, 0
        if self.package is None:
            return samples, 1
        for master in self.masters:
            line, width = [], 0
            for name in SAMPLE:
                glyph = self.package.findName(name)
                layer = glyph.findLayer(master) if glyph is not None else None
                if layer is None or layer.isNull:
                    continue
                line.append((name, outline(layer), layer.advanceWidth))
                width += layer.advanceWidth
            samples[master] = line
            widest = max(widest, width)
        return samples, widest or 1

    def edit(self, master, key):
        self.edited[master][key] = self.spins[(master, key)].value
        self.refresh()

    def revert(self):
        for (master, key), spin in self.spins.items():
            spin.setValue(self.original[master][key])

    def refresh(self):
        todo = changes(self.original, self.edited)
        accent = self.palette.color(QtGui.QPalette.Link).name()
        for (master, key), spin in self.spins.items():
            changed = self.original[master][key] != self.edited[master][key]
            spin.setStyleSheet(f"color: {accent}; font-weight: bold;" if changed else "")
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            self.subtitle.setText(f"{len(self.masters)} master{'s' if len(self.masters) != 1 else ''}, drawn with "
                                  f"{' '.join(SAMPLE)} from each master's outlines")
        count = sum(len(v) for v in todo.values())
        self.status.setText(f"{count} change{'s' if count != 1 else ''} in {len(todo)} master{'s' if len(todo) != 1 else ''}"
                            if todo else "No changes")
        self.apply_button.setEnabled(bool(todo))
        self.revert_button.setEnabled(bool(todo))
        self.diagram.update()

    def apply(self):
        todo = changes(self.original, self.edited)
        result = run(self.package, todo)
        self.last_result = result
        fontlab.UpdateAll()
        self.original = read_metrics(self.package)
        self.edited = {m: dict(v) for m, v in self.original.items()}
        self.refresh()
        self.status.setText(f"Wrote {result['values']} values in {result['masters']} masters")

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        self.samples = {}
        getattr(sys, "_fontlab_samples", {}).pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = VerticalMetrics(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
