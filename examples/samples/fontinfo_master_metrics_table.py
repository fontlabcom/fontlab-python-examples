#FLM: Font Info · Master Metrics Table
# this_file: samples/fontinfo_master_metrics_table.py
"""Edit ascender, descender, x-height and cap-height across masters; diagram follows the selected row.

Preview changes before applying to the active font.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Master Metrics Table"
KEY = "fontinfo_master_metrics_table"


def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def write_changes(package, changes):
    """Apply prevalidated (master or None, attribute, old, new) edits; restore on failure."""
    changes = [entry for entry in changes if entry[2] != entry[3]]
    if not changes:
        return {"changed": 0}
    original = package.master
    fontlab.flItems().notifyChangesApplied(TITLE, [package])
    completed = []
    try:
        for master, field, old, new in changes:
            if master is not None:
                package.setMaster(master)
            setattr(package.info, field, new)
            completed.append((master, field, old, new))
    except Exception:
        for master, field, old, new in reversed(completed):
            if master is not None:
                package.setMaster(master)
            setattr(package.info, field, old)
        raise
    finally:
        package.setMaster(original)
        fontlab.flItems().notifyChangesApplied(TITLE, [package])
        fontlab.UpdateAll()
    return {"changed": len(changes)}


MASTER_FIELDS = ["ascender", "descender", "xHeight", "capHeight"]


def validate_metrics(values):
    if not all(math.isfinite(v) and -32768 <= v <= 32767 for v in values):
        raise ValueError("Use finite metrics between −32768 and 32767.")
    asc, desc, xheight, cap = values
    if not desc <= 0 <= xheight <= cap <= asc:
        raise ValueError("Expected descender ≤ 0 ≤ x-height ≤ cap-height ≤ ascender.")
    return values


def master_values(package):
    original = package.master
    result = []
    try:
        for master in package.masters:
            package.setMaster(master)
            result.append(
                (master, [getattr(package.info, key) for key in MASTER_FIELDS])
            )
    finally:
        package.setMaster(original)
    return result


def run(package, rows):
    old = dict(master_values(package))
    changes = []
    for master, values in rows:
        validate_metrics(values)
        changes.extend(
            (master, key, previous, value)
            for key, previous, value in zip(MASTER_FIELDS, old[master], values)
        )
    return write_changes(package, changes)


class Diagram(QtGui.QWidget):
    def __init__(self, owner):
        QtGui.QWidget.__init__(self, owner)
        self.owner = owner
        self._paint_error = ""
        self.setMinimumHeight(160)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        try:
            rows = self.owner.edited_rows()
            if not rows:
                return
            row = max(0, self.owner.table.currentRow())
            _master, values = rows[row]
            asc, desc, xheight, cap = values
            span = max(1, asc - desc)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            ink = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
            line = QtGui.QColor(ink)
            line.setAlpha(90)
            band = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
            band.setAlpha(40)
            accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))

            def to_y(value):
                return 18 + (asc - value) / span * (self.height - 36)

            # x-height band: the lowercase zone between baseline and x-height
            painter.fillRect(QtCore.QRectF(150, to_y(xheight), self.width - 170, to_y(0) - to_y(xheight)), band)
            for label, value in [
                ("Ascender", asc),
                ("Cap", cap),
                ("x-height", xheight),
                ("Baseline", 0),
                ("Descender", desc),
            ]:
                y = to_y(value)
                painter.setPen(QtGui.QPen(QtGui.QBrush(accent if value == 0 else line), 1.0))
                painter.drawLine(QtCore.QPointF(150, y), QtCore.QPointF(self.width - 20, y))
                painter.setPen(ink)
                painter.drawText(QtCore.QPointF(8, y + 4), f"{label} {value:g}")
            painter.drawText(QtCore.QPointF(150, self.height - 4), f"{_master} master")
        except Exception as error:  # noqa: BLE001 - contain every PythonQt callback error
            self._paint_error = repr(error)  # an escaping exception with a live QPainter crashes FontLab
            self.owner.status.setText(self._paint_error)
        finally:
            painter.end()


class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.package = current_package()
        self._connections = []
        self.setWindowTitle(TITLE)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self.setMinimumWidth(700)
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        face = heading.font
        face.setPointSizeF(face.pointSizeF() * 1.35)
        face.setBold(True)
        heading.setFont(face)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel(
            "Edit ascender, descender, x-height and cap-height across masters; diagram follows the selected row."
            if self.package
            else "Open a font, then reopen this tool."
        )
        self.subtitle.setWordWrap(True)
        root.addWidget(self.subtitle)
        self.form = QtGui.QGridLayout()
        root.addLayout(self.form)
        self.table = QtGui.QTableWidget()
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(230)
        root.addWidget(self.table, 1)
        self.content = root
        self.status = QtGui.QLabel("")
        self.status.setWordWrap(True)
        muted = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
        muted.setAlpha(170)
        self.status.setStyleSheet("color: " + muted.name(QtGui.QColor.HexArgb))
        self.subtitle.setStyleSheet("color: " + muted.name(QtGui.QColor.HexArgb))
        footer = QtGui.QHBoxLayout()
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setAutoDefault(False)  # keep Apply as the default button
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self.apply_button.setEnabled(self.package is not None)
        self.safe(lambda: (self.setup(), self.refresh()))

    def safe(self, action):
        try:
            return action()
        except Exception as error:  # noqa: BLE001 - contain every PythonQt callback error
            self.status.setText(str(error))
            self.apply_button.setEnabled(False)

    def _connect(self, signal, slot):
        guarded = lambda *args: self.safe(lambda: slot(*args))
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def ensure_font(self):
        active = current_package()
        if active is None or active.id != self.package.id:
            raise ValueError("Activate the original font and reopen this tool.")

    def rows(self, headings, rows):
        self.table.setColumnCount(len(headings))
        self.table.setHorizontalHeaderLabels(headings)
        self.table.setRowCount(len(rows))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                item = QtGui.QTableWidgetItem(str(value))
                if isinstance(value, (float, int)):
                    item.setTextAlignment(
                        int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                    )
                self.table.setItem(row, column, item)

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:  # noqa: BLE001, S110 - already disconnected during native teardown
                pass
        self._connections = []
        windows = getattr(sys, "_fontlab_samples", {})
        if windows.get(KEY) is self:
            windows.pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)

    def setup(self):
        self.initial = master_values(self.package) if self.package else []
        self.rows(
            ["Master", "Ascender", "Descender", "x-height", "Cap height"],
            [[master] + values for master, values in self.initial],
        )
        for row in range(self.table.rowCount):
            self.table.item(row, 0).setFlags(
                int(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            )
        self.table.setEditTriggers(
            QtGui.QAbstractItemView.DoubleClicked
            | QtGui.QAbstractItemView.EditKeyPressed
        )
        self.diagram = Diagram(self)
        self.content.insertWidget(4, self.diagram)
        self._connect(self.table.itemChanged, lambda *a: self.refresh())
        self._connect(self.table.currentCellChanged, lambda *a: self.diagram.update())
        if self.initial:
            self.table.setCurrentCell(0, 1)

    def edited_rows(self):
        return [
            (
                master,
                validate_metrics(
                    [float(self.table.item(row, col).text()) for col in range(1, 5)]
                ),
            )
            for row, (master, _) in enumerate(self.initial)
        ]

    def refresh(self):
        if self.package is None:
            return
        self.ensure_font()
        rows = self.edited_rows()
        self.apply_button.setEnabled(rows != master_values(self.package))
        self.status.setText(
            "Double-click a number to edit. All rows are validated before Apply."
        )
        self.diagram.update()

    def apply(self):
        self.ensure_font()
        self.last_result = run(self.package, self.edited_rows())
        self.refresh()
        self.status.setText(f"Applied {self.last_result['changed']} metric fields")


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = Dialog(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
