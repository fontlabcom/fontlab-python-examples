# this_file: Scripts/Tools/Localized Font Names.py
# SPDX-License-Identifier: Apache-2.0
"""What: Draft localized typographic family and subfamily names for a font build.
How: Prefill from current-master package names, with family/style fallback.
Only the current master is read; the tool never changes the active master.
Escape Windows UTF-16 name strings and export an OpenType feature fragment.
Why: Keep language-specific name IDs 16 and 17 separate from legacy names.
Usage: Refresh, enter translations and a Windows language ID, then Export New.
Include the resulting .fea in an AFDKO makeotf or fontmake feature file;
inspect the compiled
name table. This tool does not install a translation or edit the open font.
Benefit: Produce build input instead of changing global application language.
Export or explicitly discard edited translations before closing. Language IDs
are decimal or 0x-prefixed; the tool checks range, not language registration.
Syntax: https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html#9.e

Setup: FontLab 9, Python 3.11, Fly and App draft_signals/qt_properties.
Modeless panel; font data, selection and application preferences stay unchanged.

Independent rewrite of the Qt i18n example idea (Qt/Riverbank Computing;
Nokia Corporation). Based on the author's own FontLab sample, Apache-2.0.
Source: rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/i18n-eca1cd9ef1528607.py
SHA256: a60c542ce24e27441a1c022e8fc57630edf380676eda4904bebc50510eb03047
Source: rescued/part2/ports/tools/pyqt-official/i18n-eca1cd9ef1528607.py
SHA256: 6253c957368cdf32b0a298001f6bb07cec0abc724e4f0918918facba0cde245f
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


TITLE = "Localized Font Names"
HELP = (
    "Translate names, set a Windows language ID and export a .fea name-table fragment."
)


def feature_string(text: str) -> str:
    """Encode non-ASCII, quote and backslash as exact UTF-16 escape units."""
    checked(text)
    if not text.strip() or any(ord(character) < 32 for character in text):
        raise ValueError("Enter a nonempty name without control characters.")
    units = text.encode("utf-16-be")
    return "".join(
        chr(unit) if 32 <= unit < 127 and unit not in (34, 92) else f"\\{unit:04x}"
        for unit in (
            int.from_bytes(units[index : index + 2], "big")
            for index in range(0, len(units), 2)
        )
    )


def name_feature(family: str, style: str, language: str, master: str) -> str:
    """Make a standalone name table fragment for IDs 16 and 17, platform 3/1."""
    try:
        lang = int(language, 16 if language.lower().startswith("0x") else 10)
    except ValueError as error:
        raise ValueError(
            "Enter a decimal or 0x-prefixed Windows language ID."
        ) from error
    if not 0 <= lang <= 65535:
        raise ValueError("Windows language ID must be in 0..65535.")
    heading = f"# Current master: {json.dumps(checked(master), ensure_ascii=True)}\n"
    return heading + (
        f'table name {{\n  nameid 16 3 1 0x{lang:04x} "{feature_string(family)}";\n'
        f'  nameid 17 3 1 0x{lang:04x} "{feature_string(style)}";\n}} name;\n'
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
            self.unsaved = False
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

        def mark_edited(self, *args: Any) -> None:
            """Keep authored translations open until exported or discarded."""
            self.unsaved = True
            self.status_line.setText(
                "Translation changed. Export New before closing, or Discard and Close."
            )

        def refresh_info(self) -> None:
            """Read current font names; preserve edited translation fields."""
            if self.unsaved:
                self.status_line.setText(
                    "Export or discard the translation before Refresh."
                )
                return
            try:
                self.info = capture_info()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.info = None
                self.master_line.setText("Current master: —")
                self.preview.setPlainText("")
                self.status_line.setText(str(error))
                return
            self.master_line.setText(f"Current master: {self.info[0]}")
            self.family_field.setText(
                self.info[1]["openTypeNamePreferredFamilyName"]
                or self.info[1]["familyName"]
            )
            self.style_field.setText(
                self.info[1]["openTypeNamePreferredSubfamilyName"]
                or self.info[1]["styleName"]
            )
            self.unsaved = False
            try:
                self.preview.setPlainText(self.build_output())
                self.status_line.setText(HELP)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.preview.setPlainText("")
                self.status_line.setText(str(error))

        def build_output(self) -> str:
            """Build from the complete captured names and current controls."""
            if self.info is None:
                raise ValueError("Refresh from an open font first.")
            return name_feature(
                str(properties.value(self.family_field, "text")),
                str(properties.value(self.style_field, "text")),
                str(properties.value(self.language_field, "text")),
                self.info[0],
            )

        def save_output(self) -> None:
            """Export a complete result; never save an old preview after failure."""
            try:
                content = checked(self.build_output())
                export_new(str(properties.value(self.destination, "text")), content)
                self.preview.setPlainText(content)
                self.unsaved = False
                self.status_line.setText(
                    "Output exported. Existing files are never overwritten."
                )
            except (ValueError, RuntimeError, OSError) as error:
                self.status_line.setText(str(error))

        def discard_close(self) -> None:
            """Explicitly discard local translations, then close normally."""
            self.unsaved = False
            self.close()

        def release_owner(self) -> None:
            """Fence callbacks when FontLab destroys the native parent."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Refuse loss of translations; retain failed cleanup for retry."""
            if self.unsaved:
                self.status_line.setText("Export New, or Discard and Close.")
                event.ignore()
                return
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
        panel.family_field = panel.add_field(
            "Localized typographic family (name ID 16)"
        )
        panel.style_field = panel.add_field(
            "Localized typographic subfamily (name ID 17)"
        )
        panel.language_field = panel.add_field(
            "Windows language ID (decimal or 0x-prefixed)"
        )
        for field in (panel.family_field, panel.style_field, panel.language_field):
            panel.scope.connect(field.textChanged, panel.mark_edited)
        panel.preview = gui.QPlainTextEdit(panel)
        panel.preview.setReadOnly(True)
        panel.stack.addWidget(panel.preview)
        panel.destination = panel.add_field("New output file (absolute path)")
        panel.add_button("Refresh Current Font", panel.refresh_info)
        panel.add_button("Export New", panel.save_output)
        panel.add_button("Discard and Close", panel.discard_close)
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
