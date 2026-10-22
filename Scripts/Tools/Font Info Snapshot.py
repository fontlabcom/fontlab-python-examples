# this_file: Scripts/Tools/Font Info Snapshot.py
# SPDX-License-Identifier: Apache-2.0
"""What: Save and compare current-master naming and credit settings as JSON.
How: Capture package naming, version, PostScript and credit text. Export a versioned
snapshot. Load a previous snapshot and compare it against fresh current data.
Why: Explicit files make name-setting changes visible across font revisions.
Usage: Refresh and Export New to save. Enter a saved snapshot's absolute path
and Compare Saved to inspect each changed field. No settings are applied.
Benefit: Reuse the saved JSON in this tool or a font build check.
Only the current master is read. Comparisons across masters are refused.
This naming snapshot is not a whole-font backup. UTF-8 BOM and CR line endings
are detected from input bytes; only actual conversions are reported.

Setup: FontLab 9, Python 3.11, Fly and App draft_signals/qt_properties.
Modeless panel; font data, selection and application preferences stay unchanged.

Independent rewrite of the Qt settingseditor example idea (Qt/Riverbank Computing;
Nokia Corporation). Based on the author's own FontLab sample, Apache-2.0.
Historical source: rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/settingseditor-9e41e71c41b116a8.py
SHA256: 1a35d9d5b3989ba7728ce129fea1bcc98cce4b221f59cf8916788ffe0ab53475
Historical source: rescued/part2/ports/tools/pyqt-official/settingseditor-9e41e71c41b116a8.py
SHA256: 1433012d1ff11a45c6414df8c625c99fc9e17cd93a91d7bc4e518ebfac5dd890
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


TITLE = "Font Info Snapshot"
HELP = (
    "Refresh, export a JSON snapshot or compare a saved snapshot with the current font."
)


def snapshot_json(captured: Capture) -> str:
    """Serialize current-master naming and credits with schema version 2."""
    master, info = captured
    if not isinstance(master, str) or not master.strip():
        raise ValueError("Snapshot requires a named master.")
    checked(master)
    if set(info) != set(FIELDS) or not all(isinstance(v, str) for v in info.values()):
        raise ValueError("Snapshot must contain exactly the declared text fields.")
    for value in info.values():
        checked(value)
    return (
        json.dumps(
            {"schema": 2, "master": master, "names": info}, ensure_ascii=True, indent=2
        )
        + "\n"
    )


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Refuse duplicate JSON keys rather than silently losing a setting."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_snapshot(filename: str) -> tuple[Capture, tuple[str, ...]]:
    """Read schema 2 as data and report only detected byte conversions."""
    path = Path(filename).expanduser()
    if not path.is_absolute():
        raise ValueError("Enter an absolute saved snapshot path.")
    raw = path.read_bytes()
    conversions = []
    if raw.startswith(b"\xef\xbb\xbf"):
        conversions.append("UTF-8 BOM removed")
    if b"\r" in raw:
        conversions.append("CR line endings normalized")
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    data = json.loads(text, object_pairs_hook=unique_object)
    if (
        not isinstance(data, dict)
        or set(data) != {"schema", "master", "names"}
        or type(data["schema"]) is not int
        or data["schema"] != 2
        or not isinstance(data["master"], str)
        or not isinstance(data["names"], dict)
    ):
        raise ValueError("Expected current-master font-name snapshot schema 2.")
    captured = (data["master"], data["names"])
    snapshot_json(captured)
    return captured, tuple(conversions)


def compare_info(saved: Capture, current: Capture) -> str:
    """Compare naming text only when both snapshots identify the same master."""
    snapshot_json(saved)
    snapshot_json(current)
    if saved[0] != current[0]:
        raise ValueError("Cannot compare snapshots across masters.")
    changes = {
        key: {"saved": saved[1][key], "current": current[1][key]}
        for key in FIELDS
        if saved[1][key] != current[1][key]
    }
    return (
        json.dumps(
            {"master": current[0], "changes": changes}, ensure_ascii=True, indent=2
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
            return snapshot_json(self.info)

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

        def compare_saved(self) -> None:
            """Compare against fresh font data; contain IO and format errors."""
            try:
                saved, conversions = read_snapshot(
                    str(properties.value(self.reference_field, "text"))
                )
                self.info = capture_info()
                self.master_line.setText(f"Current master: {self.info[0]}")
                self.preview.setPlainText(compare_info(saved, self.info))
                self.status_line.setText(
                    "Comparison shown. Export New saves the current snapshot."
                    + (" " + "; ".join(conversions) + "." if conversions else "")
                )
            except (ValueError, RuntimeError, OSError) as error:
                self.preview.setPlainText("")
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
        panel.reference_field = panel.add_field(
            "Saved snapshot to compare (absolute path)"
        )
        panel.preview = gui.QPlainTextEdit(panel)
        panel.preview.setReadOnly(True)
        panel.stack.addWidget(panel.preview)
        panel.destination = panel.add_field("New output file (absolute path)")
        panel.add_button("Refresh Current Font", panel.refresh_info)
        panel.add_button("Export New", panel.save_output)
        panel.add_button("Compare Saved", panel.compare_saved)
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
