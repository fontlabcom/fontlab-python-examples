#FLM: Reports · Glyph Table CSV
# this_file: samples/report_glyph_table_csv.py
"""A sortable table of glyphs (name, Unicode, width per master, contours, components) with CSV export.

Pick all glyphs or the selection, review the table, then export it as a
UTF-8 CSV file (choose the path first) or copy it to the clipboard for a
spreadsheet. Contours count everything drawn, components included, on the
current master. Nothing in the font changes.
"""

import csv
import io
import os
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Glyph Table CSV"
KEY = "report_glyph_table_csv"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def selected_names():
    """Glyph names selected in the Font window, in font order."""
    try:
        import FL

        font = FL.fl.font
        return [font[i].name for i in range(len(font)) if FL.fl.Selected(i)]
    except Exception:
        return []


def component_names(layer):
    names = []
    for shape in layer.shapes:
        base = shape.shapeData.componentGlyph if shape.shapeData is not None else ""
        if base:
            names.append(base)
    return names


# ---------------------------------------------------------------- core
def table(package, names):
    """(header, rows) with one row per glyph; widths per master, counts on the current master."""
    masters = list(package.masters)
    header = ["glyph", "unicode"] + [f"width {m}" for m in masters] + ["contours", "components"]
    rows = []
    for name in names:
        glyph = package.findName(name)
        if glyph is None:
            continue
        codes = " ".join(f"{c:04X}" for c in glyph.fgGlyph.unicodes)
        widths = []
        for master in masters:
            layer = glyph.findLayer(master)
            widths.append(round(layer.advanceWidth, 2) if layer is not None else "")
        layer = glyph.findLayer(package.master)
        contours = len(layer.getContours()) if layer is not None else 0
        components = " ".join(component_names(layer)) if layer is not None else ""
        rows.append([name, codes] + widths + [contours, components])
    return header, rows


def to_csv(header, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


def write_csv(path, header, rows):
    """Write the CSV (UTF-8 with BOM so spreadsheets detect it); returns the byte size."""
    with open(path, "w", encoding="utf-8-sig", newline="") as handle:
        handle.write(to_csv(header, rows))
    return os.path.getsize(path)


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class GlyphTable(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(640)
        self.resize(720, 600)
        self._connections = []
        self.package = current_package()
        self.selection = selected_names() if self.package else []
        self.header, self.rows = [], []
        self.chooser = None

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
        self.scope.addItem("All glyphs")
        self.scope.addItem(f"Selected glyphs ({len(self.selection)})")
        self.path = QtGui.QLineEdit()
        self.path.setPlaceholderText("Choose where to save the CSV…")
        self.choose_button = QtGui.QPushButton("Choose…")
        form.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        form.addWidget(self.scope, 0, 1, 1, 2)
        form.addWidget(QtGui.QLabel("File"), 1, 0)
        form.addWidget(self.path, 1, 1)
        form.addWidget(self.choose_button, 1, 2)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 0)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.copy_button = QtGui.QPushButton("Copy CSV")
        self.close_button = QtGui.QPushButton("Close")
        self.export_button = QtGui.QPushButton("Export")
        self.export_button.setDefault(True)
        footer.addWidget(self.copy_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.export_button)
        root.addLayout(footer)

        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.path.textChanged, lambda *a: self.update_buttons())
        self._connect(self.choose_button.clicked, lambda *a: self.choose())
        self._connect(self.copy_button.clicked, lambda *a: self.copy())
        self._connect(self.export_button.clicked, lambda *a: self.export())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        if len(self.selection) > 1:
            self.scope.setCurrentIndex(1)
        self.refresh()

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

    def refresh(self):
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.update_buttons()
            return
        font = fontlab.CurrentFont()
        names = [g.name for g in font.glyphs] if self.scope.currentIndex == 0 else self.selection
        self.header, self.rows = table(self.package, names)
        self.subtitle.setText(f"{len(self.rows)} glyphs · widths for {len(self.package.masters)} masters · "
                              f"contours and components on {self.package.master}. Click a header to sort.")
        self.table.setSortingEnabled(False)
        self.table.clear()
        self.table.setColumnCount(len(self.header))
        self.table.setHorizontalHeaderLabels(self.header)
        self.table.setRowCount(len(self.rows))
        for row, values in enumerate(self.rows):
            for column, value in enumerate(values):
                item = QtGui.QTableWidgetItem()
                if isinstance(value, (int, float)):
                    item.setData(QtCore.Qt.DisplayRole, value)
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                else:
                    item.setText(str(value))
                self.table.setItem(row, column, item)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setSortingEnabled(True)
        self.update_buttons()

    def update_buttons(self):
        self.export_button.setEnabled(bool(self.rows) and bool(self.path.text.strip()))
        self.copy_button.setEnabled(bool(self.rows))
        if not self.path.text.strip():
            self.status.setText("Choose a file to export, or copy the CSV.")

    def choose(self):
        """Non-modal save dialog; the chosen path lands in the File field."""
        self.chooser = QtGui.QFileDialog(self, "Export glyph table", self.path.text or "glyphs.csv",
                                         "CSV files (*.csv)")
        self.chooser.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        self.chooser.setDefaultSuffix("csv")
        self._connect(self.chooser.fileSelected, lambda path, *a: self.path.setText(path))
        self.chooser.open()

    def copy(self):
        QtGui.QApplication.clipboard().setText(to_csv(self.header, self.rows))
        self.status.setText(f"Copied {len(self.rows)} rows")

    def export(self, path=None):
        path = path or self.path.text.strip()
        size = write_csv(path, self.header, self.rows)
        self.last_result = {"path": path, "rows": len(self.rows), "bytes": size}
        self.status.setText(f"Wrote {len(self.rows)} rows to {os.path.basename(path)}")
        return path

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
    dialog = GlyphTable(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
