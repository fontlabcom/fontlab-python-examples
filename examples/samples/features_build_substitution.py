#FLM: OpenType · Suffix Substitution Builder
# this_file: samples/features_build_substitution.py
"""Preview a font-wide suffix substitution. Append to source only; compile and test in the Features panel.

Standalone PythonQt tool; feature data is shared by all masters.
"""

import re
import sys

import fontlab
from PythonQt import QtCore, QtGui


def current_package():
    package = fontlab.flWorkspace.instance().currentPackage
    return package if package is not None and not package.isNull else None


def glyph_names():
    font = fontlab.CurrentFont()
    return sorted(g.name for g in font.glyphs) if font is not None else []


def safe_name(name):
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.\-]*|\.notdef", name))  # FEA names may contain hyphens


def suffix_pairs(names, suffix):
    suffix = suffix.lstrip(".")
    known = set(names)
    ending = "." + suffix
    return [(name[:-len(ending)], name) for name in sorted(known)
            if suffix and name.endswith(ending) and name[:-len(ending)] in known
            and safe_name(name) and safe_name(name[:-len(ending)])]


def feature_text(tag, pairs):
    if not re.fullmatch(r"[A-Za-z0-9]{4}", tag):
        raise ValueError("Feature tag must contain four ASCII letters or digits.")
    lines = ["    sub " + base + " by " + target + ";"
             for base, target in pairs]
    return "feature " + tag + " {\n" + "\n".join(lines) + "\n} " + tag + ";"


def muted(widget):
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))  # copy before setAlpha
    color.setAlpha(160)
    return color.name(QtGui.QColor.HexArgb)

TITLE = 'Suffix Substitution Builder'
KEY = "features_build_substitution"
SUBTITLE = 'Preview a font-wide suffix substitution. Append to source only; compile and test in the Features panel.'
ACTION = 'Append to feature'


def append_code(old, tag, pairs):
    """Insert before a complete feature's closing tag, preserving existing source."""
    if not pairs:
        raise ValueError("No valid base / alternate pairs for this suffix.")
    snippet = feature_text(tag, pairs)
    if not old.strip():
        return snippet
    closing = re.search(r"}\s*" + re.escape(tag) + r"\s*;\s*$", old)
    if not closing:
        raise ValueError("Existing feature has no simple closing tag; copy the preview instead.")
    statements = snippet.split("{\n", 1)[1].rsplit("\n}", 1)[0]
    if any(re.search(r"\bsub\s+" + re.escape(base) + r"\s+by\b", re.sub(r"#[^\n]*", "", old)) for base, _ in pairs):
        raise ValueError("Existing feature already substitutes a source glyph; review it manually.")
    return old[:closing.start()].rstrip() + "\n" + statements + "\n" + old[closing.start():]


def run(package, layout, tag, old, new):
    if current_package() is None or current_package().id != package.id:
        raise ValueError("Activate the original font before applying.")
    if (layout.get_feature(tag) or "") != old:
        raise ValueError("Feature source changed; refresh the preview before applying.")
    names = set(glyph_names())
    referenced = re.findall(r"^\s*sub\s+(\S+)\s+by\s+(\S+);", new, re.MULTILINE)
    if any(base not in names or target not in names for base, target in referenced):
        raise ValueError("Referenced glyphs changed; reopen this tool to rebuild the preview.")
    items = [package]
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    layout.set_feature(tag, new)
    fontlab.flItems().notifyChangesApplied(TITLE, items)
    fontlab.UpdateAll()
    return {"tag": tag, "code": layout.get_feature(tag)}


class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self._connections = []
        self.package = current_package()
        self.font_data = fontlab.CurrentFont() if self.package else None
        self.names = glyph_names() if self.package else []
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
        form = QtGui.QGridLayout()
        self.suffix = QtGui.QLineEdit("sc")
        self.tag = QtGui.QLineEdit("smcp")
        self.tag.setMaxLength(4)
        form.addWidget(QtGui.QLabel("Suffix"), 0, 0)
        form.addWidget(self.suffix, 0, 1)
        form.addWidget(QtGui.QLabel("Feature tag"), 0, 2)
        form.addWidget(self.tag, 0, 3)
        root.addLayout(form)
        self.table = self.make_table(["Base", "Alternate"])
        root.addWidget(self.table, 1)
        self.code = QtGui.QPlainTextEdit()
        mono = QtGui.QFont("Menlo")
        mono.setStyleHint(QtGui.QFont.Monospace)
        self.code.setFont(mono)
        self.code.setReadOnly(True)
        root.addWidget(self.code, 1)
        self.copy_button = QtGui.QPushButton("Copy preview")
        root.addWidget(self.copy_button)
        self._connect(self.copy_button.clicked, lambda *a: self.copy_text(self.code.toPlainText()))
        self._connect(self.suffix.textChanged, lambda *a: self.refresh())
        self._connect(self.tag.textChanged, lambda *a: self.refresh())
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
        self.pairs = suffix_pairs(self.names, self.suffix.text.strip())
        self.fill(self.pairs)
        tag = self.tag.text.strip()
        self.apply_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.old_code = ""
        self.new_code = ""
        try:
            snippet = feature_text(tag, self.pairs)
            self.code.setPlainText(snippet)
            self.copy_button.setEnabled(bool(self.pairs))
            if not self.font_data:
                self.status.setText("Open a font first.")
                return
            self.old_code = self.font_data.features.get_feature(tag) or ""
            self.new_code = append_code(self.old_code, tag, self.pairs)
        except ValueError as error:
            self.status.setText(str(error))
            return
        self.code.setPlainText(self.new_code)
        self.apply_button.setEnabled(True)
        self.status.setText(f"{len(self.pairs)} pairs · font-wide, all masters · existing code preserved")

    def apply(self):
        if self.new_code:
            self.last_result = run(self.package, self.font_data.features, self.tag.text.strip(),
                                   self.old_code, self.new_code)
            self.refresh()
            self.status.setText("Feature source appended. Compile it in the Features panel to test.")

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
