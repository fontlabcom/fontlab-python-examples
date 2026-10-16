#FLM: OpenType · Feature Code Inspector
# this_file: samples/features_code_viewer.py
"""Read-only feature source for the whole font. Choose a feature and search its code.

Standalone PythonQt tool; feature data is shared by all masters.
"""

import html
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

TITLE = 'Feature Code Inspector'
KEY = "features_code_viewer"
SUBTITLE = 'Read-only feature source for the whole font. Choose a feature and search its code.'
ACTION = 'Find next'


def run(layout):
    return [(str(tag), layout.get_feature(tag) or "") for tag in layout.keys()]


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
        self.feature = QtGui.QComboBox()
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText("Search in the selected feature…")
        root.addWidget(self.feature)
        root.addWidget(self.search)
        self.code = QtGui.QTextEdit()
        self.code.setReadOnly(True)
        self.code.setAcceptRichText(False)
        root.addWidget(self.code, 1)
        self.sources = [("Prefix / languagesystems", "")]
        if self.font_data:
            self.sources = [("Prefix / languagesystems", self.font_data.features.get_prefix() or "")]
            self.sources += run(self.font_data.features)
        for tag, _ in self.sources:
            self.feature.addItem(tag)
        self._connect(self.feature.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.search.textChanged, lambda *a: self.highlight())
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


    def refresh(self):
        self.code.setPlainText(self.sources[self.feature.currentIndex][1])
        self.highlight()
        self.apply_button.setEnabled(bool(self.package and self.search.text))

    def highlight(self):
        text = self.sources[self.feature.currentIndex][1]
        needle = self.search.text
        self.match_count = 0
        chunks = []
        position = 0
        if needle:
            background = self.palette.color(QtGui.QPalette.Highlight).name()
            foreground = self.palette.color(QtGui.QPalette.HighlightedText).name()
            for match in re.finditer(re.escape(needle), text, re.IGNORECASE):
                chunks.append(html.escape(text[position:match.start()]))
                chunks.append('<span style="background-color:' + background + ';color:' + foreground + '">' +
                              html.escape(match.group()) + '</span>')
                position = match.end()
                self.match_count += 1
        chunks.append(html.escape(text[position:]))
        self.code.setHtml('<pre style="white-space:pre-wrap">' + ''.join(chunks) + '</pre>')
        self.status.setText(f"{len(self.sources) - 1} features · {self.match_count} search matches")
        self.apply_button.setEnabled(bool(needle and self.package))

    def apply(self):
        if not self.search.text:
            return
        if not self.code.find(self.search.text):
            cursor = self.code.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            self.code.setTextCursor(cursor)
            self.code.find(self.search.text)
        self.last_result = {"matches": self.match_count}

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
