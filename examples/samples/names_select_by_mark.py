#FLM: Names · Select by Mark
# this_file: samples/names_select_by_mark.py
"""Select glyphs in the Font window by their mark colour.

Lists every mark colour used in the font (and unmarked glyphs) with a
swatch and a count. Pick one or more rows and click Select, or double-click
a row. Optionally add to the current selection. Nothing in the font changes.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Select by Mark"
KEY = "names_select_by_mark"
HUES = [(15, "red"), (45, "orange"), (70, "yellow"), (160, "green"), (200, "teal"), (255, "blue"),
        (290, "purple"), (335, "pink"), (361, "red")]


# ---------------------------------------------------------------- font access
def font_marks():
    """[(glyph name, mark)] for the current font, in font order."""
    font = fontlab.CurrentFont()
    return [(g.name, int(g.mark or 0)) for g in font.glyphs] if font is not None else []


def font_window_selection():
    import FL

    font = FL.fl.font
    return [font[i].name for i in range(len(font)) if FL.fl.Selected(i)]


def select_in_font_window(names, add=False):
    """Select `names` in the Font window (replacing or adding); returns the selected count."""
    import FL

    font = FL.fl.font
    wanted = set(names)
    if not add:
        FL.fl.Unselect()
    for i in range(len(font)):
        if font[i].name in wanted:
            FL.fl.Select(i)
    fontlab.UpdateAll()
    return sum(1 for i in range(len(font)) if FL.fl.Selected(i))


# ---------------------------------------------------------------- core
def mark_color(mark, lightness=150):
    """The QColor FontLab shows for a mark value, or None for no mark."""
    if mark <= 0:
        return None
    if mark <= 360:
        return QtGui.QColor.fromHsl(mark - 1, 200, lightness)
    grey = min(255, lightness // 2 + max(0, mark - 1000) // 2)
    return QtGui.QColor(grey, grey, grey)


def mark_label(mark):
    if mark <= 0:
        return "Unmarked"
    if mark > 360:
        return f"Grey {mark - 1000}"
    hue = mark - 1
    return next(name for limit, name in HUES if hue < limit).capitalize() + f" (hue {hue}°)"


def groups(marks):
    """[(mark, [names])], marked colours by hue first, unmarked last."""
    out = {}
    for name, mark in marks:
        out.setdefault(mark, []).append(name)
    return sorted(out.items(), key=lambda item: (item[0] == 0, item[0]))


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def swatch(mark, size=16):
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtGui.QColor(0, 0, 0, 0))
    painter = QtGui.QPainter(pixmap)
    try:
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        color = mark_color(mark)
        if color is None:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(128, 128, 128)), 1.0, QtCore.Qt.DashLine))
            painter.drawRoundedRect(QtCore.QRectF(1, 1, size - 2, size - 2), 4, 4)
        else:
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(color))
            painter.drawRoundedRect(QtCore.QRectF(0, 0, size, size), 4, 4)
    finally:
        painter.end()
    return QtGui.QIcon(pixmap)


class SelectByMark(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(520)
        self.resize(540, 460)
        self._connections = []
        self.groups = []

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

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Mark", "Glyphs", "Examples"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setIconSize(QtCore.QSize(16, 16))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)

        self.add = QtGui.QCheckBox("Add to the current selection")
        root.addWidget(self.add)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload")
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select")
        self.select_button.setDefault(True)
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.table.cellDoubleClicked, lambda row, *a: self.select_rows([row]))
        self._connect(self.select_button.clicked, lambda *a: self.select_rows())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.reload()

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

    def reload(self):
        marks = font_marks()
        self.groups = groups(marks)
        if not marks:
            self.subtitle.setText("Open a font first.")
        else:
            marked = sum(len(names) for mark, names in self.groups if mark)
            self.subtitle.setText(f"{marked} of {len(marks)} glyphs carry a mark. Pick colours and click Select "
                                  "(or double-click a row).")
        self.table.setRowCount(len(self.groups))
        for row, (mark, names) in enumerate(self.groups):
            label = QtGui.QTableWidgetItem(swatch(mark), mark_label(mark))
            count = QtGui.QTableWidgetItem(str(len(names)))
            count.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
            sample = QtGui.QTableWidgetItem(" ".join(names[:6]) + (" …" if len(names) > 6 else ""))
            sample.setForeground(QtGui.QBrush(self.palette.color(QtGui.QPalette.Link)))
            for column, item in enumerate((label, count, sample)):
                self.table.setItem(row, column, item)
        self.select_button.setEnabled(bool(self.groups))
        self.status.setText(f"{len(self.groups)} mark value{'s' if len(self.groups) != 1 else ''}")

    def select_rows(self, rows=None):
        if rows is None:
            rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()})
        names = [name for row in rows if 0 <= row < len(self.groups) for name in self.groups[row][1]]
        if not names:
            self.status.setText("Pick at least one row first.")
            return
        count = select_in_font_window(names, self.add.isChecked())
        self.last_result = {"marks": [self.groups[r][0] for r in rows], "names": names, "selected": count}
        self.status.setText(f"Selected {count} glyph{'s' if count != 1 else ''}")

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
    dialog = SelectByMark(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
