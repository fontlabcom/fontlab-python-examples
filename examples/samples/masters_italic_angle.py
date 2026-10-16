#FLM: Masters · Italic Angle
# this_file: samples/masters_italic_angle.py
"""Read and set the italic angle of every master, with a painted gauge comparing them.

Edit the angles in the table (FontLab convention: negative leans right) and Apply. FontLab
stores the angle per master but only exposes the current master's value, so each master is made
current while it is read or written and the original master is restored. This is font info:
Edit > Undo does not cover it.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Italic Angle"
KEY = "masters_italic_angle"


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


# ---------------------------------------------------------------- core
def read_angles(package, masters):
    current, angles = package.master, {}
    try:
        for master in masters:
            if package.master != master:
                package.setMaster(master)
            angles[master] = float(package.italicAngle_value)
    finally:
        if package.master != current:
            package.setMaster(current)
    return angles


def write_angles(package, angles):
    """Set {master: angle}; returns the masters that changed. Restores the current master."""
    current, changed = package.master, []
    try:
        for master, angle in angles.items():
            if package.master != master:
                package.setMaster(master)
            if float(package.italicAngle_value) != angle:
                package.italicAngle_value = angle
                changed.append(master)
    finally:
        if package.master != current:
            package.setMaster(current, True)
    return changed


# ---------------------------------------------------------------- GUI kit
def muted(widget, alpha=150):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
    color.setAlpha(alpha)
    return color.name(QtGui.QColor.HexArgb)


def make_table(headers, min_height=280):
    table = QtGui.QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
    table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
    header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
    table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    table.setMinimumHeight(min_height)
    return table


def compact(spin, width=150):
    """Spin boxes read better at a fixed width than stretched across the form."""
    spin.setAlignment(QtCore.Qt.AlignRight)
    spin.setMaximumWidth(width)
    return readable(spin)


def readable(spin):
    """Spin box values render pale in FontLab's inactive palette: pin the text to WindowText."""
    spin.setStyleSheet(f"color: {spin.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText).name()};")
    return spin


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


class Gauge(QtGui.QWidget):
    """A baseline with one slanted stem line per master, labelled with its angle."""

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.report, self._paint_error = None, ""
        self.setMinimumHeight(170)
        self.angles = []  # [(master, angle)]

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
        if not self.angles:
            return
        text = QtGui.QColor(palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
        faint = QtGui.QColor(text)
        faint.setAlpha(60)
        base_y, height = self.height - 30, self.height - 64
        slot = self.width / len(self.angles)
        painter.setPen(faint)
        painter.drawLine(QtCore.QPointF(12, base_y), QtCore.QPointF(self.width - 12, base_y))
        colors = series_colors(self, len(self.angles))
        for i, ((master, angle), color) in enumerate(zip(self.angles, colors)):
            x = slot * (i + 0.5)
            painter.setPen(faint)
            painter.drawLine(QtCore.QPointF(x, base_y), QtCore.QPointF(x, base_y - height))
            top = QtCore.QPointF(x - math.tan(math.radians(angle)) * height, base_y - height)
            pen = QtGui.QPen(color)
            pen.setWidthF(3)
            pen.setCapStyle(QtCore.Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(QtCore.QPointF(x, base_y), top)
            painter.setPen(text)
            painter.drawText(QtCore.QRectF(x - slot / 2, base_y + 6, slot, 18), int(QtCore.Qt.AlignHCenter),
                             f"{master}  {angle:g}°")


class ItalicAngle(SampleDialog):
    def build(self):
        self.table = make_table(["Master", "Italic angle"], 120)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.root.addWidget(self.table, 1)
        self.gauge = Gauge()
        self.gauge.report = self.paint_report
        self.root.addWidget(self.gauge, 1)
        self.spins = {}
        if self.package is None:
            return
        angles = read_angles(self.package, self.masters)
        self.table.setRowCount(len(self.masters))
        for row, master in enumerate(self.masters):
            label = QtGui.QTableWidgetItem(master + ("  (current)" if master == self.current_master else ""))
            label.setForeground(QtGui.QBrush(self.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText)))
            self.table.setItem(row, 0, label)
            spin = QtGui.QDoubleSpinBox()
            spin.setRange(-45, 45)
            spin.setDecimals(1)
            spin.setSuffix("°")
            spin.setValue(angles[master])
            compact(spin, 120)
            self._connect(spin.valueChanged, lambda *a: self.refresh())
            self.table.setCellWidget(row, 1, spin)
            self.spins[master] = spin
        self.saved = angles

    def edited(self):
        return {m: spin.value for m, spin in self.spins.items()}

    def refresh(self):
        if not hasattr(self, "gauge"):
            return
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        self.subtitle.setText(f"{len(self.masters)} masters · negative angles lean right")
        edited = self.edited()
        self.gauge.angles = [(m, edited[m]) for m in self.masters]
        self.gauge.update()
        pending = [m for m in self.masters if edited[m] != self.saved.get(m)]
        self.apply_button.setEnabled(bool(pending))
        self.status.setText(f"{len(pending)} master{'s' if len(pending) != 1 else ''} changed" if pending else
                            "Edit an angle to change it")

    def apply(self):
        changed = write_angles(self.package, self.edited())
        self.saved = read_angles(self.package, self.masters)
        fontlab.UpdateAll()
        self.last_result = {"changed": changed, "angles": dict(self.saved)}
        self.refresh()
        self.status.setText(f"Set the italic angle of {len(changed)} masters")


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = ItalicAngle(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
