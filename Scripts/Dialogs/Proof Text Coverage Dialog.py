# this_file: Scripts/Dialogs/Proof Text Coverage Dialog.py
# SPDX-License-Identifier: Apache-2.0
"""Check proof text against current-font Unicode assignments.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Click Enter Proof Text to open a modeless standard input dialog. Accept to inspect coverage; Cancel keeps the existing draft. Preview reads the current font again. Duplicate assignments remain visible.
Why: Use a modeless text dialog and normalize Qt UTF-16 text.
Benefit: Find missing characters and ambiguous assignments before proofing.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank standarddialogs dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
Archived replacements: Apache-2.0, own earlier work. Upstream BSD headers and
collection GPL metadata have unresolved scope. No upstream code or assets copied.
The two archived variants consolidate into this FontLab-specific workflow;
original sample controls are not a claim of feature parity. Native acceptance pending.
Historical source: rescued/part2/ports/dialogs/pyqt-official/standarddialogs-e1a0a829f8f2e311.py
SHA256: 4a705367140cd7600706cf7ab7522523ddc7c5cd3592309c78d316b67cfc0055
Historical source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/standarddialogs-e1a0a829f8f2e311.py
SHA256: 80b66bcc88b46955f88d0b31040a2ea4cdf272aa6de1f825c9ff189abf21af22
"""

from time import monotonic
from typing import Any


def glyph_rows() -> tuple[tuple[str, tuple[int, ...]], ...]:
    """Adapt App's fenced table. Refuse a missing font or a partial observation.

    The existing App helper owns native double reads and package/font/master
    fences. Convert its Unicode display column under the same deadline only.
    """
    from fly.ap.glyph_catalog import capture

    deadline = monotonic() + 2.0
    table = capture(deadline=deadline)
    rows: list[tuple[str, tuple[int, ...]]] = []
    for name, codes, _stamp in table.rows:
        if monotonic() >= deadline:
            raise TimeoutError("Font scan expired; no partial result.")
        scalars = tuple(int(token.removeprefix("U+"), 16) for token in codes.split())
        if any(0xD800 <= code <= 0xDFFF for code in scalars):
            raise ValueError("Unreadable Unicode scalar assignment.")
        rows.append((name, scalars))
    if monotonic() >= deadline:
        raise TimeoutError("Font scan expired; no partial result.")
    return tuple(rows)


def coverage(rows: tuple[tuple[str, tuple[int, ...]], ...], text: str) -> str:
    """Report each proof character once, in occurrence order, with all names."""
    text = text.encode("utf-16", "surrogatepass").decode("utf-16", "replace")
    if not text:
        raise ValueError("Enter nonempty proof text.")
    mapping: dict[int, list[str]] = {}
    for name, codes in rows:
        for code in dict.fromkeys(codes):
            mapping.setdefault(code, []).append(name)
    return "\n".join(
        f"U+{ord(c):04X}  " + ", ".join(mapping.get(ord(c), ["MISSING"]))
        for c in dict.fromkeys(text)
    )


def main() -> Any:
    """Open a retained, owned panel through Fly and the existing App lifecycle."""
    from fly import qt
    from fly.ap.scripting import names_dialog_type, show_script_dialog

    g = qt.QtGui
    base = names_dialog_type()

    class Dialog(base):
        """Keep local settings and guard every callback at the App boundary."""

        def __init__(self, parent: Any) -> None:
            base.__init__(
                self,
                parent,
                "Proof Text Coverage Dialog",
                "dialogs_standarddialogs",
            )
            self.subtitle.setText(
                "Click Enter Proof Text to open a modeless standard input dialog. Accept to inspect coverage; Cancel keeps the existing draft. Preview reads the current font again. Duplicate assignments remain visible."
            )
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.extra_outputs: list[Any] = []
            self.status = g.QLabel("Ready. Preview uses the current font.")
            self.status.setWordWrap(True)
            self.draft = "Hamburgefontsiv"
            self.input_dialog = g.QInputDialog(self)
            self.input_dialog.setWindowTitle("Proof Text")
            self.input_dialog.setLabelText("Text to check against the current font")
            self.input_dialog.setTextValue(self.draft)
            button = g.QPushButton("Enter Proof Text")
            self.root.addWidget(button)
            self.root.addWidget(self.output)
            self._connect(button.clicked, lambda *a: self.input_dialog.show())
            self._connect(self.input_dialog.textValueSelected, self.accept_text)
            preview = g.QPushButton("Preview / Refresh")
            close = g.QPushButton("Close")
            self.root.addWidget(preview)
            self.root.addWidget(self.status)
            self.root.addWidget(close)
            self._connect(preview.clicked, lambda *a: self.preview())
            self._connect(close.clicked, lambda *a: self.close())
            self.resize(660, 520)

        def preview(self) -> bool:
            """Clear old output first. Publish complete results or a useful refusal."""
            self.output.setPlainText("")
            for editor in self.extra_outputs:
                editor.setPlainText("")
            try:
                text = coverage(glyph_rows(), self.draft)
                self.output.setPlainText(text)
                self.status.setText(
                    "Preview complete. Select text and copy; refresh after font changes."
                )
                return True
            except Exception as error:  # noqa: BLE001 - contain native UI callback failures
                self.output.setPlainText("")
                for editor in self.extra_outputs:
                    editor.setPlainText("")
                self.status.setText(str(error))
                return False

        def accept_text(self, text: str) -> None:
            """Adopt accepted text only; Cancel leaves the local draft intact."""
            self.draft = text
            self.preview()

        def closeEvent(self, event: Any) -> None:
            """The base disconnects child signals before deleting this parent."""
            self.input_dialog.hide()
            base.closeEvent(self, event)

    return show_script_dialog(Dialog, "dialogs_standarddialogs")


if __name__ == "__main__":
    main()
