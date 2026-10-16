#FLM: Reports · Nodes Near Zones
# this_file: samples/report_nodes_near_zones.py
"""Find on-curve nodes that sit within a few units of a vertical metric but not on it.

Near misses (y = 687 when the cap height is 688) are almost always slips
of the mouse; real overshoots are further away and pass. Checks baseline,
x-height, cap height, ascender and descender of every master. Select the
glyphs to fix them. Nothing in the font changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Nodes Near Zones"
KEY = "report_nodes_near_zones"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def selected_names():
    try:
        import FL

        font = FL.fl.font
        return [font[i].name for i in range(len(font)) if FL.fl.Selected(i)]
    except Exception:
        return []


def select_in_font_window(names):
    import FL

    font = FL.fl.font
    wanted = set(names)
    FL.fl.Unselect()
    for i in range(len(font)):
        if font[i].name in wanted:
            FL.fl.Select(i)
    fontlab.UpdateAll()
    return [font[i].name for i in range(len(font)) if FL.fl.Selected(i)]


def master_metrics(package, master):
    """[(label, y)] vertical metrics of one master."""
    m = fontlab.FontMetrics(package, master)
    return [("baseline", 0.0), ("x-height", m.xHeight), ("cap height", m.capsHeight),
            ("ascender", m.ascender), ("descender", m.descender)]


def on_curve_points(layer):
    """[(x, y)] of the layer's own on-curve nodes with each shape's transform applied."""
    points = []
    for shape in layer.shapes:
        if shape.shapeData is not None and shape.shapeData.componentGlyph:
            continue
        transform = shape.transform
        for contour in shape.getContours():
            for node in contour.nodes():
                if node.isOn():
                    p = transform.map(QtCore.QPointF(node.x, node.y))
                    points.append((p.x(), p.y()))
    return points


# ---------------------------------------------------------------- core
def near_misses(points, metrics, tolerance):
    """[(label, metric y, node x, node y)] for points with 0 < |y - metric| <= tolerance."""
    out = []
    for x, y in points:
        for label, value in metrics:
            delta = y - value
            if 0 < abs(delta) <= tolerance:
                out.append((label, value, x, y))
    return out


def scan(package, names, tolerance):
    """[(glyph, master, metric label, metric y, node x, node y)]."""
    masters = list(package.masters)
    metrics = {m: master_metrics(package, m) for m in masters}
    rows = []
    for name in names:
        glyph = package.findName(name)
        if glyph is None:
            continue
        for master in masters:
            layer = glyph.findLayer(master)
            if layer is None:
                continue
            for hit in near_misses(on_curve_points(layer), metrics[master], tolerance):
                rows.append((name, master) + hit)
    return rows


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class NodesNearZones(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(560)
        self.resize(600, 500)
        self._connections = []
        self.rows = []
        self.package = current_package()
        self.selection = selected_names() if self.package else []

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
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Selected glyphs ({len(self.selection)})")
        self.scope.addItem("All glyphs")
        self.tolerance = QtGui.QSpinBox()
        self.tolerance.setRange(1, 30)
        self.tolerance.setValue(4)
        self.tolerance.setSuffix(" units")
        self.tolerance.setAlignment(QtCore.Qt.AlignRight)
        form.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        form.addWidget(self.scope, 0, 1)
        form.addWidget(QtGui.QLabel("Within"), 0, 2)
        form.addWidget(self.tolerance, 0, 3)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Glyph · master", "Metric", "Node", "y", "Off by"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.rescan_button = QtGui.QPushButton("Rescan")
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select glyphs")
        self.select_button.setDefault(True)
        footer.addWidget(self.rescan_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.scope.currentIndexChanged, lambda *a: self.rescan())
        self._connect(self.tolerance.valueChanged, lambda *a: self.rescan())
        self._connect(self.rescan_button.clicked, lambda *a: self.rescan())
        self._connect(self.select_button.clicked, lambda *a: self.select_rows())
        self._connect(self.table.cellDoubleClicked, lambda row, *a: self.select_rows([row]))
        self._connect(self.close_button.clicked, lambda *a: self.close())
        if not self.selection:
            self.scope.setCurrentIndex(1)
        self.rescan()

    def _connect(self, signal, slot):
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:  # an exception escaping a PythonQt slot can take FontLab down
                self.slot_error = repr(error)
                label = getattr(self, "status", None)
                if label is not None:
                    label.setText("Error: " + self.slot_error)
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def rescan(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.select_button.setEnabled(False)
            return
        font = fontlab.CurrentFont()
        names = self.selection if self.scope.currentIndex == 0 else [g.name for g in font.glyphs]
        tolerance = self.tolerance.value
        self.rows = scan(self.package, names, tolerance)
        glyphs = sorted({r[0] for r in self.rows})
        self.subtitle.setText(f"{len(names)} glyphs × {len(self.package.masters)} masters checked: on-curve nodes "
                              f"1–{tolerance} units off baseline, x-height, cap height, ascender or descender.")
        alert = QtGui.QColor("#d33")
        self.table.setRowCount(len(self.rows))
        for row, (name, master, label, value, x, y) in enumerate(self.rows):
            cells = [f"{name} · {master}", f"{label} {value:g}", f"{x:g}, {y:g}", f"{y:g}", f"{y - value:+g}"]
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                if column >= 2:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if column == 4:
                    item.setForeground(QtGui.QBrush(alert))
                self.table.setItem(row, column, item)
        self.select_button.setEnabled(bool(self.rows))
        self.status.setText(f"{len(self.rows)} near miss{'es' if len(self.rows) != 1 else ''} in "
                            f"{len(glyphs)} glyph{'s' if len(glyphs) != 1 else ''}")

    def select_rows(self, rows=None):
        if rows is None:
            rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()})
            rows = rows or list(range(len(self.rows)))
        names = [self.rows[r][0] for r in rows if 0 <= r < len(self.rows)]
        selected = select_in_font_window(names)
        self.last_result = {"selected": selected}
        self.status.setText(f"Selected {len(selected)} glyph{'s' if len(selected) != 1 else ''}")

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
    dialog = NodesNearZones(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
