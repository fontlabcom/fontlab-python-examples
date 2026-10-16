#FLM: Font Info · Names & Credits
# this_file: samples/fontinfo_names_editor.py
"""Edit family, style, credits and version naming for the current font.

Family, designer, copyright and version name are font-wide; the style name belongs
to the current master (FontLab stores it per master). A table previews the changed
fields before Apply.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Names & Credits"
KEY = "fontinfo_names_editor"


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


FIELDS = [
    ("familyName", "Family"),
    ("styleName", "Style"),
    ("openTypeNameDesigner", "Designer"),
    ("copyright", "Copyright"),
    ("openTypeNameVersion", "Version name"),
]


def validate_names(values):
    for field in ("familyName", "styleName"):
        if not values[field].strip():
            raise ValueError("Family and style must not be blank.")
    if any(any(ord(c) < 32 for c in text) for text in values.values()):
        raise ValueError("Use single-line text without control characters.")
    if not re.fullmatch(
        r"Version [0-9]+\.[0-9]{1,3}(?:[ ;].*)?", values["openTypeNameVersion"]
    ):
        raise ValueError(
            "Version name must start with Version major.minor (1–3 minor digits)."
        )
    return values


def run(package, values):
    validate_names(values)
    return write_changes(
        package, [(None, k, getattr(package.info, k) or "", v) for k, v in values.items()]
    )


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
            "Edit family, style, credits and version naming for the current font."
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
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
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
        self.fields = {}
        for row, (field, title) in enumerate(FIELDS):
            edit = QtGui.QLineEdit(
                str(getattr(self.package.info, field) or "") if self.package else ""
            )
            self.fields[field] = edit
            if field == "styleName" and self.package:  # style name is stored per master (measured)
                title = f"Style ({self.package.master} master)"
            self.form.addWidget(QtGui.QLabel(title), row, 0)
            self.form.addWidget(edit, row, 1)
            self._connect(edit.textChanged, lambda *a: self.refresh())

    def values(self):
        return validate_names({key: edit.text for key, edit in self.fields.items()})

    def refresh(self):
        if self.package is None:
            return
        self.ensure_font()
        values = self.values()
        changes = [
            (label, getattr(self.package.info, field) or "", values[field])
            for field, label in FIELDS
            if (getattr(self.package.info, field) or "") != values[field]
        ]
        self.rows(["Field", "Current", "Proposed"], changes)
        self.apply_button.setEnabled(bool(changes))
        self.status.setText(f"{len(changes)} fields changed · style name applies to the current master only")

    def apply(self):
        self.ensure_font()
        self.last_result = run(self.package, self.values())
        self.refresh()
        self.status.setText(f"Applied {self.last_result['changed']} fields")


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
