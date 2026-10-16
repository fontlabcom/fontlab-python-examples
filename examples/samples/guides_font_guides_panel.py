#FLM: Guides · Font Guides Panel
# this_file: samples/guides_font_guides_panel.py
"""Show the font's guides and add one named guide to every master of the selected glyphs.

FontLab 9.0.9783 does not let Python add font-wide guides: flPackage.guidelines is
read-only, its items are bare flObjects (names only), and fontgate fgFont.guides
edits do not reach the document (measured). So this panel lists the font guide
names it can see and adds the guide as a glyph guide instead, saying so in the UI.
Auto layers are skipped. One Apply is one Undo step.
"""

import math
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Font Guides Panel"
KEY = "guides_font_guides_panel"


# ---------------------------------------------------------------- font access
def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    if package is None or package.isNull:
        return None
    return package


def selected_glyphs(package):
    """flGlyphs selected in the Font window, in font order; else the current glyph."""
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
    glyphs = [package.findName(name) for name in names]
    return [g for g in glyphs if g is not None]


def master_layers(glyph, masters):
    """[(master, flLayer)] for the masters present in this glyph."""
    found = []
    for master in masters:
        layer = glyph.findLayer(master)
        if layer is not None and not layer.isNull:
            found.append((master, layer))
    return found


def font_guide_names(package):
    """Names of the current master's font guides: flPackage.guidelines yields flObjects without geometry."""
    names = []
    for item in package.guidelines:
        try:
            names.append(str(item.name) or "(unnamed)")
        except Exception:
            names.append("?")
    return names


# ---------------------------------------------------------------- guides
# flGuideLine(QLineF, flags, style): the (angle, point) overload ignores the angle in PythonQt and
# makes free "vector" guides; FontLab's own glyph guides carry these flags (flsnapline.h).
HORIZONTAL, VERTICAL, VECTOR = 0x2000, 0x4000, 0x1000  # flSnaps::Horizontal / Vertical / Vector
GLYPH_GUIDE = 0x102  # SnapObjectsStyle gsGlyphGuideline


def guide_record(guide):
    """(x, y, angle in degrees, name) of an flGuideLine; x is 0 for horizontal, y for vertical guides."""
    point = guide.centerPoint
    angle = round(math.degrees(guide.angle), 2) % 180  # flGuideLine.angle is in radians
    x, y = round(point.x(), 2), round(point.y(), 2)
    return (0.0 if angle == 0 else x, 0.0 if angle == 90 else y, angle, str(guide.name or ""))


def glyph_guides(layer):
    return [g for g in layer.guidelines if not g.isHint]


def new_guide(values):
    """A glyph guide through (x, y) at `angle` degrees (0 horizontal, 90 vertical)."""
    x, y, angle, name = values
    if angle == 0:
        line, flags = QtCore.QLineF(x, y, x + 100, y), HORIZONTAL
    elif angle == 90:
        line, flags = QtCore.QLineF(x, y, x, y + 100), VERTICAL
    else:
        radians = math.radians(angle)
        line, flags = QtCore.QLineF(x, y, x + 100 * math.cos(radians), y + 100 * math.sin(radians)), VECTOR
    guide = fontlab.flGuideLine(line, flags, GLYPH_GUIDE)
    guide.name = name
    return guide


def add_guides(jobs):
    """jobs: [(glyph, layer, [records to add])]. Notify before and after: one Undo step."""
    layers = [layer for _, layer, values in jobs if values]
    glyphs = []
    for glyph, _, values in jobs:
        if values and glyph not in glyphs:
            glyphs.append(glyph)
    if not layers:
        return {"layers": 0, "guides": 0}
    items = layers + glyphs
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    count = 0
    for _, layer, values in jobs:
        if values:
            layer.appendGuidelines([new_guide(v) for v in values])
            count += len(values)
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    fontlab.UpdateAll()
    return {"layers": len(layers), "guides": count}


# ---------------------------------------------------------------- GUI
def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class FontGuidesPanel(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(540)
        palette = self.palette
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setStyleSheet("QAbstractSpinBox, QAbstractItemView { color: %s }" % palette.color(QtGui.QPalette.WindowText).name())
        self._connections = []
        self.last_result = None
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.masters = list(self.package.masters) if self.package else []
        self.current_master = self.package.master if self.package else ""

        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.font_guides = QtGui.QLabel()
        self.font_guides.setWordWrap(True)
        root.addWidget(self.font_guides)
        self.notice = QtGui.QLabel("Python cannot add font-wide guides in this FontLab build, so the guide "
                                   "below is added to the selected glyphs as a glyph guide on every chosen master.")
        self.notice.setWordWrap(True)
        self.notice.setStyleSheet(f"color: {self.palette.color(QtGui.QPalette.Link).name()};")
        root.addWidget(self.notice)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.direction = QtGui.QComboBox()
        self.direction.addItems(["Horizontal", "Vertical"])
        self.position = QtGui.QSpinBox()
        self.position.setRange(-5000, 5000)
        self.position.setSuffix(" units")
        self.position.setAlignment(QtCore.Qt.AlignRight)
        self.guide_name = QtGui.QLineEdit()
        self.guide_name.setPlaceholderText("guide name")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Direction"), 0, 0)
        form.addWidget(self.direction, 0, 1)
        form.addWidget(QtGui.QLabel("Position"), 0, 2)
        form.addWidget(self.position, 0, 3)
        form.addWidget(QtGui.QLabel("Name"), 1, 0)
        form.addWidget(self.guide_name, 1, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Glyph · master", "Glyph guides now", "Action"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(180)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Add glyph guide")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self._connect(self.direction.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.position.valueChanged, lambda *a: self.refresh())
        self._connect(self.guide_name.textChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal, slot):
        def guarded(*args):
            try:
                slot(*args)
            except Exception as error:  # an exception escaping a PythonQt slot can take FontLab down
                self.status.setText(f"Error: {error}")
        signal.connect(guarded)
        self._connections.append((signal, guarded))

    # state
    def chosen_masters(self):
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def record(self):
        value = float(self.position.value)
        name = self.guide_name.text.strip()
        return (0.0, value, 0.0, name) if self.direction.currentIndex == 0 else (value, 0.0, 90.0, name)

    def plan(self):
        """[(glyph, master, layer, guide count, action)]; action is add / exists / auto layer."""
        record = self.record()
        planned = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()):
                existing = [guide_record(g) for g in glyph_guides(layer)]
                action = "auto layer, skipped" if layer.autoLayer else "exists" if record in existing else "add"
                planned.append((glyph, master, layer, len(existing), action))
        return planned

    def refresh(self):
        if self.package is None:
            self.font_guides.setText("Open a font first.")
        else:
            names = font_guide_names(self.package)
            listed = ", ".join(names) if names else "none"
            self.font_guides.setText(f"Font guides in {self.current_master}: {listed}")
        count = len(self.glyphs)
        if self.package is not None and not count:
            self.subtitle.setText("Select glyphs in the Font window, then run this script again.")
        elif count:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (" …" if count > 8 else "")
            self.subtitle.setText(f"{count} glyph{'s' if count != 1 else ''}: {names}")
        rows = [(f"{g.name} · {m}", str(n), action) for g, m, layer, n, action in (self.plan() if self.glyphs else [])]
        ink = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(rows))
        for row, cells in enumerate(rows):
            for column, text in enumerate(cells):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(QtGui.QBrush(accent if column == 2 and text == "add" else ink))
                if column == 1:
                    item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
                self.table.setItem(row, column, item)
        adds = sum(1 for cells in rows if cells[2] == "add")
        named = bool(self.guide_name.text.strip())
        self.apply_button.setEnabled(adds > 0 and named)
        self.status.setText(f"{adds} layer{'s' if adds != 1 else ''} to change" if named else "Name the guide to add it")

    def apply(self):
        record = self.record()
        jobs = [(g, layer, [record]) for g, m, layer, n, action in self.plan() if action == "add"]
        self.last_result = add_guides(jobs)
        self.refresh()
        self.status.setText(f"Added {self.last_result['guides']} glyph guides")

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
    dialog = FontGuidesPanel(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
