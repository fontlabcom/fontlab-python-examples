# this_file: Scripts/Tools/Font Name Encoding Audit.py
# SPDX-License-Identifier: Apache-2.0
"""What: Audit current-master naming and credit fields for legacy encoding support.
How: Read the package fields and master twice. Test ASCII, Windows-1252 and
Mac Roman; include a UTF-16-BE byte dump. Report each unencodable code point.
PostScript font names are ASCII-required. Only the current master is read.
Why: Silent replacement characters damage legacy name-table exports.
Usage: Open a font, Refresh Current Font, inspect the JSON and Export New.
Benefit: Give font build scripts a reproducible encoding report.
The fields are source metadata, not the compiled binary name table.

Setup: FontLab 9, Python 3.11, Fly and App draft_signals/qt_properties.
Modeless panel; font data, selection and application preferences stay unchanged.

Independent rewrite of the Qt codecs example idea (Qt/Riverbank Computing;
Nokia Corporation). Based on the author's own FontLab sample, Apache-2.0.
Source: rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/codecs-19571722ed96aa9c.py
SHA256: c39fb1bab6762e4b2286af604794547e07de9f5a680b4c671e7882c9a6ac9470
Source: rescued/part2/ports/tools/pyqt-official/codecs-19571722ed96aa9c.py
SHA256: fe2257ea8123a18e3995ca919937fd16a02845c939d2ea695fd99cea327cd3a9
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

Capture = tuple[str, dict[str, str]]
_PANELS: list[Any] = []
FIELDS = (
    "familyName",
    "styleName",
    "openTypeNamePreferredFamilyName",
    "openTypeNamePreferredSubfamilyName",
    "copyright",
    "trademark",
    "postscriptFontName",
    "postscriptFullName",
    "openTypeNameCompatibleFullName",
    "styleMapFamilyName",
    "styleMapStyleName",
    "openTypeNameDesigner",
    "openTypeNameManufacturer",
    "openTypeNameVersion",
)


def checked(text: str) -> str:
    """Refuse text that the Qt bridge can change or UTF-8 cannot encode."""
    if any(c in text for c in ("\0", "\r", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("Text contains NUL, CR, NBSP or a Unicode line separator.")
    try:
        text.encode("utf-8")
    except UnicodeError as error:
        raise ValueError("Text contains an invalid Unicode surrogate.") from error
    return text


def capture_info(native: Any = None) -> Capture:
    """Read naming text and master twice from one fenced workspace package.

    Use flPackage.info for the current master's values. Refuse package,
    master or field changes during capture. Other masters remain untouched.
    """
    if native is None:
        from fly import fl

        native = fl
    workspace = native.flWorkspace.instance()
    package = workspace.currentPackage
    if package is None or package.isNull:
        raise ValueError("Open a font first.")
    package_id = int(package.id)
    snapshots: list[Capture] = []
    for _ in range(2):
        current = workspace.currentPackage
        if current is None or current.isNull or int(current.id) != package_id:
            raise ValueError("Current font changed; retry.")
        master = current.master
        if not isinstance(master, str) or not master.strip():
            raise ValueError("Current master must have a name.")
        master = checked(master)
        info = current.info
        values = {field: getattr(info, field) for field in FIELDS}
        if not all(isinstance(value, str) for value in values.values()):
            raise ValueError("Font naming fields must contain text.")
        snapshots.append(
            (master, {field: checked(value) for field, value in values.items()})
        )
        current = workspace.currentPackage
        if (
            current is None
            or current.isNull
            or int(current.id) != package_id
            or current.master != master
        ):
            raise ValueError("Current font or master changed; retry.")
    if snapshots[0] != snapshots[1]:
        raise ValueError("Font names or master changed during capture; retry.")
    return snapshots[0]


def export_new(filename: str, text: str) -> None:
    """Write exact UTF-8 to a new absolute file; refuse overwrite and symlinks."""
    path = Path(filename).expanduser()
    if not path.is_absolute():
        raise ValueError("Enter an absolute path to a NEW output file.")
    checked(text)
    with path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(text)


TITLE = "Font Name Encoding Audit"
HELP = "Refresh reads current-master naming and credit fields. Export a strict encoding JSON report."


def encoding_report(captured: Capture) -> str:
    """Report every strict failure index; never substitute or drop a character."""
    master, info = captured
    records = []
    for field, text in info.items():
        checked(text)
        for encoding in ("ascii", "cp1252", "mac_roman", "utf-16-be"):
            missing = []
            for index, character in enumerate(text):
                try:
                    character.encode(encoding)
                except UnicodeEncodeError:
                    missing.append(
                        {"index": index, "codepoint": f"U+{ord(character):04X}"}
                    )
            data = text.encode(encoding) if not missing else None
            records.append(
                {
                    "field": field,
                    "text": text,
                    "encoding": encoding,
                    "hex": data.hex() if data is not None else None,
                    "ascii_required": field == "postscriptFontName",
                    "ascii_valid": text.isascii()
                    if field == "postscriptFontName"
                    else None,
                    "purpose": "byte dump"
                    if encoding == "utf-16-be"
                    else "legacy encoding check",
                    "unencodable": missing,
                }
            )
    return (
        json.dumps(
            {
                "schema": 2,
                "master": master,
                "scope": f"Current master: {master}",
                "records": records,
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n"
    )


def show(qt: Any, parent: Any) -> Any:
    """Open a retained modeless panel; disconnect owned slots before deletion."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own controls and retain failed Close cleanup for a retry."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(720, 540)
            self.stack = gui.QVBoxLayout(self)
            self.stack.setContentsMargins(16, 16, 16, 16)
            self.stack.setSpacing(8)
            self.status_line = gui.QLabel(HELP, self)
            self.stack.addWidget(self.status_line)
            self.master_line = gui.QLabel("Current master: —", self)
            self.stack.addWidget(self.master_line)
            self.scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )
            self.info: Capture | None = None
            self.scope.connect(self.destroyed, lambda *args: self.release_owner())

        def add_button(self, label: str, action: Any) -> None:
            """Guard each native signal; never let exceptions cross Qt."""
            item = gui.QPushButton(label, self)
            self.stack.addWidget(item)
            self.scope.connect(item.clicked, lambda *args: action())

        def add_field(self, label: str, initial: str = "") -> Any:
            """Use separate labels so values cannot be confused with paths."""
            self.stack.addWidget(gui.QLabel(label, self))
            item = gui.QLineEdit(self)
            item.setText(initial)
            self.stack.addWidget(item)
            return item

        def refresh_info(self) -> None:
            """Read current font names; clear the result when capture fails."""
            try:
                self.info = capture_info()
                self.master_line.setText(f"Current master: {self.info[0]}")
                self.preview.setPlainText(self.build_output())
                self.status_line.setText(HELP)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.info = None
                self.master_line.setText("Current master: —")
                self.preview.setPlainText("")
                self.status_line.setText(str(error))

        def build_output(self) -> str:
            """Build from the complete captured names and current controls."""
            if self.info is None:
                raise ValueError("Refresh from an open font first.")
            return encoding_report(self.info)

        def save_output(self) -> None:
            """Export a complete result; never save an old preview after failure."""
            try:
                content = checked(self.build_output())
                export_new(str(properties.value(self.destination, "text")), content)
                self.preview.setPlainText(content)
                self.status_line.setText(
                    "Output exported. Existing files are never overwritten."
                )
            except (ValueError, RuntimeError, OSError) as error:
                self.status_line.setText(str(error))

        def release_owner(self) -> None:
            """Fence callbacks when FontLab destroys the native parent."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Disconnect slots; retain failed cleanup for a Close retry."""
            if not self.scope.finish():
                event.ignore()
                return
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.preview = gui.QPlainTextEdit(panel)
        panel.preview.setReadOnly(True)
        panel.stack.addWidget(panel.preview)
        panel.destination = panel.add_field("New output file (absolute path)")
        panel.add_button("Refresh Current Font", panel.refresh_info)
        panel.add_button("Export New", panel.save_output)
        panel.refresh_info()
        panel.show()
    except Exception as error:
        panel.status_line.setText(str(error))
        if panel.scope.finish():
            _PANELS.remove(panel)
            panel.deleteLater()
        else:
            panel.show()
        raise
    return panel


def main() -> None:
    """Use FontLab's main window and Fly; never construct an application."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
