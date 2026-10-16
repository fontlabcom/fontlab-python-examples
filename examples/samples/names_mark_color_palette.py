#FLM: Names · Mark Color Palette
# this_file: samples/names_mark_color_palette.py
"""Click a colour swatch to mark the selected glyphs with it (or clear the mark).

Each swatch shows how many glyphs in the font, and in the selection, carry
that mark. FontLab stores a mark as hue + 1 (1-360), grey as 1000 + level,
and 0 for none. One click is one Undo step.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Mark Color Palette"
KEY = "names_mark_color_palette"
PRESETS = [
    ("None", 0), ("Red", 1), ("Orange", 31), ("Yellow", 56), ("Green", 121), ("Teal", 171),
    ("Blue", 211), ("Purple", 271), ("Pink", 321), ("Grey", 1128),
]


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


def font_marks():
    """{glyph name: mark} for every glyph of the current font."""
    font = fontlab.CurrentFont()
    return {g.name: int(g.mark or 0) for g in font.glyphs} if font is not None else {}


# ---------------------------------------------------------------- core
def notify(package, glyphs):
    """One Undo step needs the same [layers + glyphs] list notified before and after the edit."""
    if glyphs:
        layers = [g.findLayer(package.master) or g.layers[0] for g in glyphs]
        layers = [layer for layer in layers if not layer.autoLayer]  # notifying auto layers re-resolves them all
        fontlab.flItems().notifyChangesApplied(TITLE, layers + glyphs)


def mark_color(mark, lightness=150):
    """The QColor FontLab shows for a mark value, or None for no mark."""
    if mark <= 0:
        return None
    if mark <= 360:
        return QtGui.QColor.fromHsl(mark - 1, 200, lightness)
    grey = min(255, lightness // 2 + max(0, mark - 1000) // 2)
    return QtGui.QColor(grey, grey, grey)


def counts(marks, names=None):
    """{mark: count} over all names, or only over `names`."""
    out = {}
    for name, mark in marks.items():
        if names is None or name in names:
            out[mark] = out.get(mark, 0) + 1
    return out


def run(package, glyphs, mark):
    """Set the glyph mark of every glyph that differs; one Undo step. Returns changed names."""
    changed = [g for g in glyphs if int(g.mark or 0) != mark]
    notify(package, changed)
    for glyph in changed:
        glyph.mark = mark
    notify(package, changed)
    return [g.name for g in changed]


# ---------------------------------------------------------------- GUI
def auto_dependants(package, names):
    """Auto composites (any auto master layer) that use one of `names` as a component."""
    wanted = set(names)
    if package is None or not wanted:
        return []
    import FL

    font, found = FL.fl.font, []
    for index in range(len(font)):
        glyph = package.findName(font[index].name)
        if glyph is None or glyph.name in wanted:
            continue
        for layer in glyph.layers:
            if layer.isMasterLayer and layer.autoLayer and any(
                    shape.isComponent and str(shape.shapeData.componentGlyph) in wanted for shape in layer.shapes):
                found.append(glyph.name)
                break
    return found


def rebuild_note(package, names, limit=5):
    """Status text naming the auto composites FontLab rebuilds when their bases are notified (fl#8512)."""
    found = auto_dependants(package, names)
    if not found:
        return ""
    shown = ", ".join(found[:limit]) + (f" +{len(found) - limit} more" if len(found) > limit else "")
    return f"FontLab will rebuild auto {shown} (anchors/locks may change; Undo does not restore them)"


def show_rebuilds(dialog, names):
    """Append the auto composites FontLab will rebuild to the dialog's status: notifying a base of
    auto composites re-resolves auto layers font-wide (AGENTS: editing a BASE of auto composites)."""
    status = getattr(dialog, "status", None)
    note = rebuild_note(dialog.package, names) if status is not None else ""
    if note:
        text = status.text
        status.setText(f"{text} · {note}" if text else note)
        # the wrapped note must not overlap the table: reserve its height, which grows the dialog
        status.setMinimumHeight(status.heightForWidth(max(status.width, 320)))


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


def swatch_style(mark, widget):
    color = mark_color(mark)
    border = widget.palette.color(QtGui.QPalette.Mid).name()
    if color is None:
        text = widget.palette.color(QtGui.QPalette.ButtonText).name()
        return (f"QPushButton {{ color: {text}; border: 1px dashed {border}; border-radius: 8px; padding: 8px; "
                f"text-align: left; }}")
    text = "#111111" if color.lightness() > 140 else "#ffffff"
    pressed = color.darker(115).name()
    return (f"QPushButton {{ background: {color.name()}; color: {text}; border: 1px solid {color.darker(120).name()};"
            f" border-radius: 8px; padding: 8px; text-align: left; }}"
            f" QPushButton:pressed {{ background: {pressed}; }}")


def dot_icon(mark, size=12):
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtGui.QColor(0, 0, 0, 0))
    color = mark_color(mark)
    painter = QtGui.QPainter(pixmap)
    try:
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if color is None:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(128, 128, 128)), 1.0))
            painter.drawEllipse(1, 1, size - 2, size - 2)
        else:
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(color))
            painter.drawEllipse(0, 0, size, size)
    finally:
        painter.end()
    return QtGui.QIcon(pixmap)


class Palette(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(500)
        self.resize(560, 420)
        self._connections = []
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []

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

        grid = QtGui.QGridLayout()
        grid.setSpacing(8)
        self.swatches = {}
        for index, (label, mark) in enumerate(PRESETS):
            button = QtGui.QPushButton(label)
            button.setMinimumHeight(48)
            button.setStyleSheet(swatch_style(mark, self))
            button.setToolTip(f"Mark value {mark}")
            grid.addWidget(button, index // 5, index % 5)
            self.swatches[mark] = button
            self._connect(button.clicked, lambda *a, m=mark: self.apply(m))
        root.addLayout(grid)

        caption = QtGui.QLabel("Selection")
        bold = caption.font
        bold.setBold(True)
        caption.setFont(bold)
        root.addWidget(caption)
        self.list = QtGui.QListWidget()
        self.list.setViewMode(QtGui.QListView.IconMode)
        self.list.setFlow(QtGui.QListView.LeftToRight)
        self.list.setWrapping(True)
        self.list.setResizeMode(QtGui.QListView.Adjust)
        self.list.setSpacing(4)
        self.list.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.list.setMinimumHeight(90)
        self.list.setIconSize(QtCore.QSize(14, 14))
        root.addWidget(self.list, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)  # the auto-composite note can be long
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload selection")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.close_button.clicked, lambda *a: self.close())
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

    def reload(self):
        self.package = current_package()
        self.glyphs = selected_glyphs(self.package) if self.package else []
        self.refresh()

    def refresh(self):
        self.refresh_listing()
        show_rebuilds(self, [g.name for g in self.glyphs])

    def refresh_listing(self):
        marks = font_marks()
        names = {g.name for g in self.glyphs}
        in_font, in_selection = counts(marks), counts(marks, names)
        for label, mark in PRESETS:
            button = self.swatches[mark]
            button.setText(f"{label}\n{in_font.get(mark, 0)} · {in_selection.get(mark, 0)} sel")
            button.setEnabled(bool(self.glyphs))
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText("Select glyphs in the Font window, then click Reload selection.")
        else:
            self.subtitle.setText(f"Click a swatch to mark the {count} selected glyph{'s' if count != 1 else ''}. "
                                  "Numbers: glyphs in the font · in the selection.")
        self.list.clear()
        for glyph in self.glyphs:
            item = QtGui.QListWidgetItem(dot_icon(marks.get(glyph.name, 0)), glyph.name)
            self.list.addItem(item)
        other = sorted(m for m in in_font if m not in self.swatches)
        extra = f" · other marks in font: {', '.join(str(m) for m in other)}" if other else ""
        self.status.setText(f"{len(marks)} glyphs in font{extra}")

    def apply(self, mark):
        changed = run(self.package, self.glyphs, mark) if self.package else []
        self.last_result = {"mark": mark, "changed": changed}
        fontlab.UpdateAll()
        self.refresh()
        label = dict((m, l) for l, m in PRESETS).get(mark, str(mark))
        self.status.setText(f"{label}: changed {len(changed)} glyph{'s' if len(changed) != 1 else ''}")

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
    dialog = Palette(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
