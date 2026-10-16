#FLM: Font Info · Bump Font Version
# this_file: samples/fontinfo_version_bumper.py
"""Bump the numeric version and version name; optionally append a dated font note.

Preview changes before applying to the active font.
"""

import sys
from datetime import date

import fontlab
from PythonQt import QtCore, QtGui

TITLE = "Bump Font Version"
KEY = "fontinfo_version_bumper"


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


LABELS = {"versionMajor": "Major version", "versionMinor": "Minor version",
          "openTypeNameVersion": "Version name", "note": "Note"}


def bumped(major, minor, mode):
    if not 0 <= minor <= 999 or not 0 <= major <= 65535:
        raise ValueError("Version must have major 0–65535 and minor 0–999.")
    new = (
        (major + 1, 0)
        if mode == "major"
        else (major + (minor == 999), (minor + 1) % 1000)
    )
    if new[0] > 65535:
        raise ValueError("The major version would exceed 65535.")
    return new


def version_plan(package, mode, dated, day):
    major, minor = bumped(int(package.versionMajor), int(package.versionMinor), mode)
    name = f"Version {major}.{minor:03d}"
    values = {"versionMajor": major, "versionMinor": minor, "openTypeNameVersion": name}
    changes = [(None, key, getattr(package.info, key), value) for key, value in values.items()]
    if dated:  # the note is stored per master (measured): append the line to every master's note
        original = package.master
        try:
            for master in package.masters:
                package.setMaster(master)
                old = str(package.info.note or "")
                changes.append((master, "note", old, old + ("\n" if old else "") + f"{day}: {name}"))
        finally:
            package.setMaster(original)
    return changes


def run(package, mode, dated, day):
    return write_changes(package, version_plan(package, mode, dated, day))


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
            "Bump the numeric version and version name; optionally append a dated font note."
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
        self.mode = QtGui.QComboBox()
        self.mode.addItems(["Minor (+0.001, carry at 999)", "Major (+1, reset minor)"])
        self.date_note = QtGui.QCheckBox("Append a dated line to every master's note")
        self.date_note.setChecked(True)
        self.form.addWidget(self.mode, 0, 0)
        self.form.addWidget(self.date_note, 0, 1)
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.date_note.toggled, lambda *a: self.refresh())

    def changes(self):
        return version_plan(
            self.package,
            "major" if self.mode.currentIndex else "minor",
            self.date_note.isChecked(),
            date.today().isoformat(),  # noqa: DTZ011 - local calendar date is intentional
        )

    def refresh(self):
        if self.package is None:
            return
        self.ensure_font()
        self.rows(
            ["Field", "Current", "Proposed"],
            [(LABELS[k] if m is None else f"{LABELS[k]} · {m}", old, new) for m, k, old, new in self.changes()],
        )
        self.apply_button.setEnabled(True)
        self.status.setText("Minor uses three digits; existing notes are preserved.")

    def apply(self):
        self.ensure_font()
        self.last_result = write_changes(self.package, self.changes())
        self.refresh()
        self.status.setText("Version applied; preview now shows the next bump.")


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
