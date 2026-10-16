#FLM: Masters · Compatibility Check
# this_file: samples/masters_compatibility_check.py
"""Check that every master of each glyph can interpolate: same contours, nodes, anchors, components.

The tree lists each glyph with ✓ or ✗; expand it to see the counts per master, with the values
that differ from the other masters highlighted. Contour structure is compared node by node
(on-curve / handle pattern), anchors by name and components by base glyph. Select the failing
glyphs in the Font window with one click. Read-only.
"""

import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Master Compatibility"
KEY = "masters_compatibility_check"


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


def master_layers(glyph, masters):
    """{master: flLayer} for the masters present in this glyph."""
    found = {}
    for master in masters:
        layer = glyph.findLayer(master)
        if layer is not None and not layer.isNull:
            found[master] = layer
    return found


def own_contours(layer):
    """Contours drawn in this layer; layer.getContours() also lists the contours of components."""
    return [contour for shape in layer.shapes if not shape.isComponent for contour in shape.contours]


def node_points(contour):
    return [(node.x, node.y, bool(node.isOn())) for node in contour.nodes()]


# ---------------------------------------------------------------- core
def signature(layer):
    """Comparable structure of a layer: contour node patterns, anchor names, component bases."""
    contours = tuple("".join("o" if on else "h" for _, _, on in node_points(c)) for c in own_contours(layer))
    anchors = tuple(sorted(a.name for a in layer.anchors))
    components = tuple(shape.shapeData.componentGlyph if hasattr(shape.shapeData, "componentGlyph") else shape.name
                       for shape in layer.shapes if shape.isComponent)
    return contours, anchors, components


def summary(sig):
    contours, anchors, components = sig
    return len(contours), sum(len(c) for c in contours), len(anchors), len(components)


def check_glyph(glyph, masters):
    """({master: signature or None for auto layers}, ok, [differing aspects])."""
    sigs = {m: (None if l.autoLayer else signature(l)) for m, l in master_layers(glyph, masters).items()}
    real = [s for s in sigs.values() if s is not None]
    problems = []
    for index, aspect in enumerate(("contours", "anchors", "components")):
        if len({s[index] for s in real}) > 1:
            problems.append(aspect)
    if len(sigs) < len(masters):
        problems.append("missing layer")
    return sigs, not problems, problems


def all_names():
    import FL

    font = FL.fl.font
    return [font[i].name for i in range(len(font))]


def select_in_font_window(names):
    import FL

    font = FL.fl.font
    wanted = set(names)
    for i in range(len(font)):
        FL.fl.Select(i, 1 if font[i].name in wanted else 0)


# ---------------------------------------------------------------- GUI kit
def muted(widget, alpha=150):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
    color.setAlpha(alpha)
    return color.name(QtGui.QColor.HexArgb)


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


class Compatibility(SampleDialog):
    ACTION = "Select ✗ Glyphs"
    COLUMNS = ["Glyph · master", "Contours", "Nodes", "Anchors", "Components", "Status"]

    def build(self):
        self.setMinimumWidth(600)
        grid = self.form()
        self.source = QtGui.QComboBox()
        self.source.addItem(f"Selected glyphs ({len(self.names)})")
        self.source.addItem("Whole font")
        self._connect(self.source.currentIndexChanged, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        grid.addWidget(self.source, 0, 1)
        grid.setColumnStretch(1, 1)
        self.tree = QtGui.QTreeWidget()
        self.tree.setColumnCount(len(self.COLUMNS))
        self.tree.setHeaderLabels(self.COLUMNS)
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setUniformRowHeights(True)
        header = self.tree.header()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtGui.QHeaderView.ResizeToContents)  # status text must not clip
        header.setStretchLastSection(False)
        self.tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tree.setMinimumHeight(300)
        self.root.addWidget(self.tree, 1)

    def refresh(self):
        self.results, self.failing = {}, []
        self.tree.clear()
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.apply_button.setEnabled(False)
            return
        names = all_names() if self.source.currentIndex == 1 else self.names
        self.subtitle.setText(f"{len(names)} glyphs across {len(self.masters)} masters: {', '.join(self.masters)}")
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link))  # copy: color() can alias the palette
        bad = QtGui.QColor("#d33")
        ink = QtGui.QBrush(self.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))
        muted_color = QtGui.QColor(self.palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText))  # copy: color() can alias the palette
        muted_color.setAlpha(130)
        right = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        for name in names:
            glyph = self.package.findName(name)
            if glyph is None:
                continue
            sigs, ok, problems = check_glyph(glyph, self.masters)
            self.results[name] = ok
            if not ok:
                self.failing.append(name)
            top = QtGui.QTreeWidgetItem(self.tree)
            top.setText(0, name)
            top.setForeground(0, ink)
            top.setText(5, "✓" if ok else "✗ " + ", ".join(problems))
            top.setTextAlignment(5, right)
            top.setForeground(5, QtGui.QBrush(muted_color if ok else bad))
            values = {m: summary(s) for m, s in sigs.items() if s is not None}
            for master, sig in sigs.items():
                child = QtGui.QTreeWidgetItem(top)
                child.setText(0, master)
                for column in range(5):
                    child.setForeground(column, ink)
                if sig is None:
                    child.setText(1, "auto layer · not compared")
                    child.setForeground(1, QtGui.QBrush(muted_color))
                    continue
                for column, value in enumerate(summary(sig), start=1):
                    child.setText(column, str(value))
                    child.setTextAlignment(column, right)
                    others = [v[column - 1] for m, v in values.items() if m != master]
                    if others and value != max(set(others), key=others.count):
                        font = child.font(column)
                        font.setBold(True)
                        child.setFont(column, font)
                        child.setForeground(column, QtGui.QBrush(accent))
            top.setExpanded(not ok)
        self.apply_button.setEnabled(bool(self.failing))
        self.status.setText(f"{len(self.failing)} of {len(self.results)} glyphs incompatible")

    def apply(self):
        select_in_font_window(self.failing)
        self.last_result = {"selected": list(self.failing)}
        fontlab.UpdateAll()
        self.status.setText(f"Selected {len(self.failing)} incompatible glyphs in the Font window")


def main():
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = Compatibility(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
