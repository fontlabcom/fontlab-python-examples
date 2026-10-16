#FLM: Reports · Open Contours
# this_file: samples/report_open_contours.py
"""Find open contours on every master and select the glyphs that have them.

Open paths are usually unintended in a font for filling: they render
unpredictably and break overlap removal. Each row is one open contour with
its master, node count and the gap between its end points. Nothing in the
font changes.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Open Contours"
KEY = "report_open_contours"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


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


# ---------------------------------------------------------------- core
def scan(package):
    """[(glyph, master, contour index, node count, gap)] for every open contour, font order."""
    font = fontlab.CurrentFont()
    masters = list(package.masters)
    out = []
    for fg in font.glyphs:
        glyph = package.findName(fg.name)
        if glyph is None:
            continue
        for master in masters:
            layer = glyph.findLayer(master)
            if layer is None:
                continue
            for index, contour in enumerate(layer.getContours()):
                if contour.closed:
                    continue
                nodes = contour.nodes()
                gap = 0.0
                if len(nodes) > 1:
                    first, last = nodes[0], nodes[len(nodes) - 1]
                    gap = math.hypot(last.x - first.x, last.y - first.y)
                out.append((fg.name, master, index, len(nodes), round(gap, 1)))
    return out


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class OpenContours(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(500)
        self.resize(540, 440)
        self._connections = []
        self.rows = []

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

        self.table = QtGui.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Glyph", "Master", "Contour", "Nodes", "End gap"])
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

        self._connect(self.rescan_button.clicked, lambda *a: self.rescan())
        self._connect(self.select_button.clicked, lambda *a: self.select_rows())
        self._connect(self.table.cellDoubleClicked, lambda row, *a: self.select_rows([row]))
        self._connect(self.close_button.clicked, lambda *a: self.close())
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
        package = current_package()
        if package is None:
            self.subtitle.setText("Open a font first.")
            self.select_button.setEnabled(False)
            return
        self.rows = scan(package)
        glyphs = sorted({r[0] for r in self.rows})
        if self.rows:
            self.subtitle.setText(f"{len(self.rows)} open contour{'s' if len(self.rows) != 1 else ''} in "
                                  f"{len(glyphs)} glyph{'s' if len(glyphs) != 1 else ''} across "
                                  f"{len(package.masters)} masters.")
        else:
            self.subtitle.setText(f"No open contours on any of {len(package.masters)} masters.")
        alert = QtGui.QColor("#d33")
        self.table.setRowCount(len(self.rows))
        for row, values in enumerate(self.rows):
            for column, value in enumerate(values):
                item = QtGui.QTableWidgetItem(str(value) if column != 2 else f"#{value + 1}")
                if column >= 2:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                if column == 4 and value > 0:
                    item.setForeground(QtGui.QBrush(alert))
                self.table.setItem(row, column, item)
        self.select_button.setEnabled(bool(self.rows))
        self.status.setText("Double-click a row to select that glyph." if self.rows else "")

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
    dialog = OpenContours(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
