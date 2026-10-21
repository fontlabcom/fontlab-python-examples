# this_file: Scripts/Dialogs/Expandable Glyph Search.py
# SPDX-License-Identifier: Apache-2.0
"""Find glyph names with optional exact and case matching.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Enter text, expand More Options if required, then click Preview. Results use fresh current-font names. Reverse changes result order only; no glyph is selected.
Why: Hide optional literal-match controls until they are needed.
Benefit: Inspect exact glyph names without changing the Font window selection.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank extension dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
Archived replacements: Apache-2.0 owner grant. Upstream BSD headers and
collection GPL metadata have unresolved scope. No upstream code or assets copied.
The two archived variants consolidate into this FontLab-specific workflow;
original sample controls are not a claim of feature parity. Native acceptance pending.
Source: rescued/part2/ports/dialogs/pyqt-official/extension-a1c26dbf9f995edb.py
SHA256: 96175cf7e19bcd1dc4f2e6664890436df05a791d47b8442411bd35bb3d32df32
Source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/extension-a1c26dbf9f995edb.py
SHA256: d662938fecf32e30d708c02bafce2e7468461be547ab33fd41c6405a6e4f94d9
"""

from time import monotonic
from typing import Any


def glyph_rows() -> tuple[tuple[str, tuple[int, ...]], ...]:
    """Adapt App's fenced table. Refuse a missing font or a partial observation.

    The existing App helper owns native double reads and package/font/master
    fences. Convert its Unicode display column under the same deadline only.
    """
    from fly.ap._glyph_catalog_native import capture

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


def search(
    names: tuple[str, ...], query: str, case: bool, exact: bool, reverse: bool
) -> tuple[str, ...]:
    """Match literal names in font order. An empty query is an explicit error."""
    if not query:
        raise ValueError("Enter part of a glyph name.")
    needle = query if case else query.casefold()

    def matches(name: str) -> bool:
        value = name if case else name.casefold()
        return value == needle if exact else needle in value

    result = tuple(name for name in names if matches(name))
    return result[::-1] if reverse else result


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
                self, parent, "Expandable Glyph Search", "dialogs_extension"
            )
            self.subtitle.setText(
                "Enter text, expand More Options if required, then click Preview. Results use fresh current-font names. Reverse changes result order only; no glyph is selected."
            )
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.extra_outputs: list[Any] = []
            self.status = g.QLabel("Ready. Preview uses the current font.")
            self.status.setWordWrap(True)
            self.query = g.QLineEdit("a")
            self.root.addWidget(g.QLabel("Glyph name contains"))
            self.root.addWidget(self.query)
            more = g.QPushButton("More Options")
            more.setCheckable(True)
            self.root.addWidget(more)
            self.options = g.QWidget()
            layout = g.QVBoxLayout(self.options)
            self.case = g.QCheckBox("Match case")
            self.exact = g.QCheckBox("Whole name")
            self.reverse = g.QCheckBox("Reverse result order")
            for control in (self.case, self.exact, self.reverse):
                layout.addWidget(control)
            self.root.addWidget(self.options)
            self.options.hide()
            self._connect(
                more.toggled, lambda checked: self.options.setVisible(bool(checked))
            )
            self.root.addWidget(self.output)
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
                text = (
                    "\n".join(
                        search(
                            tuple(n for n, _ in glyph_rows()),
                            self.query.text,
                            self.case.checked,
                            self.exact.checked,
                            self.reverse.checked,
                        )
                    )
                    or "No matching names."
                )
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

    return show_script_dialog(Dialog, "dialogs_extension")


if __name__ == "__main__":
    main()
