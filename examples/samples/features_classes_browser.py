#FLM: OpenType · OpenType Class Browser
# this_file: samples/features_classes_browser.py
"""Browse feature classes and their members. Filter by class name or glyph; font-wide across masters.

Standalone PythonQt tool; feature data is shared by all masters.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui


def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
    color.setAlpha(160)
    return color.name(QtGui.QColor.HexArgb)

TITLE = 'OpenType Class Browser'
KEY = "features_classes_browser"
SUBTITLE = 'Browse feature classes and their members. Filter by class name or glyph; font-wide across masters.'
ACTION = 'Copy class'


def run(groups):
    modes = {str(name): group.isFeaGroup() for name, group in groups.items()}
    rows = []
    for record in groups.getAsClassRecords() or []:
        name, _, body = str(record).partition(":")
        if modes.get(name):
            members = [part.rstrip("'") for part in body.split()]
            rows.append((name, len(members), " ".join(members)))
    return sorted(rows)


class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self._connections = []
        self.package = current_package()
        self.font_data = fontlab.CurrentFont() if self.package else None
        self.last_result = None
        self.setWindowTitle(TITLE)
        palette = self.palette
        ink = palette.color(QtGui.QPalette.WindowText)
        palette.setColor(QtGui.QPalette.Text, ink)  # FontLab's Text can be light on a light Base
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % ink.name())
        self.setMinimumWidth(640)
        self.resize(780, 620)
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel(SUBTITLE if self.package else "Open a font, then run this script again.")
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet("color: " + muted(self))
        root.addWidget(self.subtitle)
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet("color: " + muted(self))
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("Filter class names or members…")
        root.addWidget(self.search)
        self.table = self.make_table(["Class", "Members", "Glyph names"])
        root.addWidget(self.table, 1)
        self.members = QtGui.QPlainTextEdit()
        self.members.setReadOnly(True)
        root.addWidget(self.members, 1)
        self.all_rows = run(self.font_data.groups) if self.font_data else []
        self._connect(self.search.textChanged, lambda *a: self.refresh())
        self._connect(self.table.itemSelectionChanged, lambda *a: self.preview())
        footer = QtGui.QHBoxLayout()
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.close_button)
        self.apply_button = QtGui.QPushButton(ACTION)
        self.apply_button.setDefault(True)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._safe(self.refresh)

    def _safe(self, callback):
        try:
            callback()
        except Exception as error:
            self.status.setText(str(error))
            self.apply_button.setEnabled(False)

    def _connect(self, signal, slot):
        # Keep a plain Python receiver and contain every signal exception.
        wrapped = lambda *args: self._safe(lambda: slot(*args))
        signal.connect(wrapped)
        self._connections.append((signal, wrapped))

    def make_table(self, headers):
        table = QtGui.QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        table.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        return table

    def fill(self, rows):
        self.rows = rows
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, value in enumerate(cells):
                item = QtGui.QTableWidgetItem(str(value))
                if isinstance(value, int):
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)

    def copy_text(self, text):
        QtGui.QApplication.clipboard().setText(text)
        self.last_result = {"copied": text}
        self.status.setText("Copied feature code to the clipboard.")
    def refresh(self):
        needle = self.search.text.lower()
        self.fill([row for row in self.all_rows if needle in (row[0] + " " + row[2]).lower()])
        if self.rows:
            self.table.selectRow(0)
        self.preview()
        self.status.setText(f"{len(self.rows)} of {len(self.all_rows)} feature classes")

    def preview(self):
        row = self.table.currentRow()
        self.snippet = ""
        if 0 <= row < len(self.rows):
            name, _, members = self.rows[row]
            self.snippet = "@" + name.lstrip("@") + " = [" + members + "];"
        self.members.setPlainText(self.snippet or "No matching feature classes.")
        self.apply_button.setEnabled(bool(self.snippet))

    def apply(self):
        if self.snippet:
            self.copy_text(self.snippet)

    def closeEvent(self, event):
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self._connections = []
        windows = sys.__dict__.get("_fontlab_samples", {})
        if windows.get(KEY) is self:
            windows.pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


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
