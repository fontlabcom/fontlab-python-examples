# this_file: Scripts/Widgets/Glyph Proof Groups.py
# SPDX-License-Identifier: Apache-2.0
# historical source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/groupbox-f702b62aa47629ad.py
# historical source sha256: e9e05eb140a7fa7fadfcaa6fdfee3ab938cde45069aed0386dcd82e101ca0db0
# historical source: rescued/part2/ports/widgets/pyqt-official/groupbox-f702b62aa47629ad.py
# historical source sha256: 1a3228685ce42992156a888fad35efa8ce67f180aba6bb3727e413921e19d684
"""What: Build a glyph-name proof from useful current-font groups.
How: Read a fresh App catalog. Combine encoded and unencoded glyphs in font
order, optionally omit suffix names, then wrap slash names into short lines.
Why: Explicit groups make a compact Metrics proof without changing selection.
Usage: Tick the desired groups and set names per line. Preview, then copy the
plain text into FontLab Metrics. Dots identify suffix names by convention.
Names outside portable slash syntax are omitted and listed in the status line.
Benefit: Compare base glyphs and alternates in repeatable proof groups.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Group Box example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.
"""

import re
from typing import Any

Row = tuple[str, str, str]


def proof_groups(
    rows: tuple[Row, ...], encoded: bool, unencoded: bool, suffixes: bool, per_line: int
) -> str:
    """Keep font order and exact names. Omit names that cannot be represented in slash syntax."""
    if type(per_line) is not int or not 1 <= per_line <= 100:
        raise ValueError("Use 1 to 100 names per proof line.")
    if not encoded and not unencoded:
        raise ValueError("Enable at least one glyph group.")
    names = [
        name
        for name, codes, _ in rows
        if (encoded if codes else unencoded)
        and (suffixes or "." not in name.lstrip("."))
    ]
    if not names:
        raise ValueError("No glyphs match these groups.")
    names = [name for name in names if re.fullmatch(r"[A-Za-z0-9_.-]+", name)]
    return "\n".join(
        "".join("/" + name for name in names[start : start + per_line])
        for start in range(0, len(names), per_line)
    )


def main() -> Any:
    """Open the owned modeless App panel. Import Qt only in the host."""
    import fly.ap.qt_properties as properties
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module imports
    from fly import qt

    g = qt.QtGui
    base = scripting.names_dialog_type()

    class Dialog(base):
        """Build a reusable Metrics proof from explicit glyph groups."""

        def __init__(self, parent: Any) -> None:
            """Build labelled controls with a selectable plain-text result."""
            base.__init__(
                self, parent, "Glyph Proof Groups", "widgets_glyph_proof_groups"
            )
            self.subtitle.setText(
                "Build a slash-name proof for FontLab Metrics. Preview reads the current font."
            )
            group = g.QGroupBox("Glyph groups")
            group_layout = g.QVBoxLayout(group)
            self.encoded, self.unencoded, self.suffixes = (
                g.QCheckBox("Encoded"),
                g.QCheckBox("Unencoded"),
                g.QCheckBox("Include suffix names"),
            )
            self.encoded.setChecked(True)
            for control in (self.encoded, self.unencoded, self.suffixes):
                group_layout.addWidget(control)
            self.root.addWidget(group)
            self.per_line = g.QSpinBox()
            self.per_line.setRange(1, 100)
            self.per_line.setValue(12)
            self.root.addWidget(g.QLabel("Glyph names per line"))
            self.root.addWidget(self.per_line)
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.status = g.QLabel(
                "Choose glyph groups, then Preview to build Metrics text."
            )
            self.status.setTextFormat(qt.QtCore.Qt.PlainText)
            self.status.setWordWrap(True)
            self.root.addWidget(self.output)
            self.preview_button, self.close_button = (
                g.QPushButton("Preview / Refresh"),
                g.QPushButton("Close"),
            )
            for control in (self.preview_button, self.status, self.close_button):
                self.root.addWidget(control)
            self._connect(self.preview_button.clicked, lambda *args: self.preview())
            self._connect(self.close_button.clicked, lambda *args: self.close())
            self.resize(620, 580)

        def publish(self, text: str) -> None:
            """Publish exact result text; refuse Qt character conversion."""
            if any(c in text for c in ("\x00", "\u00a0", "\u2028", "\u2029", "\r")):
                raise ValueError(
                    "Result contains characters Qt cannot preserve exactly."
                )
            self.output.setPlainText(text)
            if str(self.output.toPlainText()) != text:
                self.output.setPlainText("")
                raise ValueError("Qt changed the result text; copy refused.")

        def preview(self) -> None:
            """Build grouped proof text and report names omitted from slash syntax."""
            self.status.setText("Building grouped proof...")
            self.output.setPlainText("")
            try:
                self.build_result()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output.setPlainText("")
                self.status.setText(str(error))

        def build_result(self) -> None:
            """Build one complete result from current controls and context."""
            import fly.ap.glyph_catalog as catalog

            rows = tuple(catalog.capture().rows)
            result = proof_groups(
                rows,
                bool(properties.value(self.encoded, "checked")),
                bool(properties.value(self.unencoded, "checked")),
                bool(properties.value(self.suffixes, "checked")),
                int(properties.value(self.per_line, "value")),
            )
            self.publish(result)
            omitted = [
                name
                for name, codes, _ in rows
                if (
                    bool(properties.value(self.encoded, "checked"))
                    if codes
                    else bool(properties.value(self.unencoded, "checked"))
                )
                and (
                    bool(properties.value(self.suffixes, "checked"))
                    or "." not in name.lstrip(".")
                )
                and not re.fullmatch(r"[A-Za-z0-9_.-]+", name)
            ]
            self.status.setText(
                "Proof ready. Copy into Metrics."
                + (
                    " Omitted: " + ", ".join(repr(name) for name in omitted)
                    if omitted
                    else ""
                )
            )

    return scripting.show_script_dialog(Dialog, "widgets_glyph_proof_groups")


if __name__ == "__main__":
    main()
