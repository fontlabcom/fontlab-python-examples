# this_file: Scripts/Dialogs/Glyph Proof Batch Wizard.py
# SPDX-License-Identifier: Apache-2.0
"""Build slash-escaped proof lines from current-font glyph names.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Choose a prefix and a line size, or paste JSON from Glyph Batch Recipe Settings. Use Next to review proof batches. Copy the result into a FontLab text workflow. Back retains your settings. The tool does not open tabs or change selection.
Why: Validate pasted recipes against a fresh font snapshot.
Benefit: Turn the settings recipe into reproducible proof lines without font edits.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank trivialwizard dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
Archived replacements: Apache-2.0, own earlier work. Upstream BSD headers and
collection GPL metadata have unresolved scope. No upstream code or assets copied.
The two archived variants consolidate into this FontLab-specific workflow;
original sample controls are not a claim of feature parity. Native acceptance pending.
Source: rescued/part2/ports/dialogs/pyqt-official/trivialwizard-c0d4a173b261a3e5.py
SHA256: 9c74350f548bafb26b39fab1126681762dc20b334036595203ec5126893c96ac
Source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/trivialwizard-c0d4a173b261a3e5.py
SHA256: 8ad810ecf2897a079286ed7b7ede6a2259c30c0fe7e6b90dc4141af0912103b5
"""

import json
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


def proof_batches(names: tuple[str, ...], prefix: str, size: int) -> str:
    """Group real names into slash-escaped lines without changing FontLab tabs."""
    if type(size) is not int or not 1 <= size <= 1000:
        raise ValueError("Line size must be an integer from 1 to 1000.")
    chosen = [name for name in names if name.startswith(prefix)]
    if not chosen:
        raise ValueError("No glyph names match the prefix.")
    if any("/" in name or any(c.isspace() for c in name) for name in chosen):
        raise ValueError("A glyph name cannot be represented in slash notation.")
    return "\n".join(
        "".join("/" + name for name in chosen[i : i + size])
        for i in range(0, len(chosen), size)
    )


def proof_from_recipe(payload: str, names: tuple[str, ...]) -> tuple[str, str, int]:
    """Consume Glyph Batch Recipe Settings JSON; refuse a stale glyph scope.

    Return proof text, prefix and batch size. The caller adopts settings only
    after the complete plan passes. JSON is data; no recipe code is executed.
    """
    plan = json.loads(payload)
    fields = {"prefix", "batch_size", "glyphs", "batches"}
    if not isinstance(plan, dict) or set(plan) != fields:
        raise ValueError("Paste a complete Glyph Batch Recipe Settings recipe.")
    prefix, size = plan["prefix"], plan["batch_size"]
    if not isinstance(prefix, str) or type(size) is not int or not 1 <= size <= 1000:
        raise ValueError("Recipe requires a text prefix and batch size from 1 to 1000.")
    chosen = [name for name in names if name.startswith(prefix)]
    if plan["glyphs"] != chosen or not chosen:
        raise ValueError("Recipe glyphs changed; regenerate the recipe from this font.")
    if (
        type(plan["batches"]) is not int
        or plan["batches"] != (len(chosen) + size - 1) // size
    ):
        raise ValueError("Recipe batch count does not match its glyph scope.")
    return proof_batches(tuple(chosen), "", size), prefix, size


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
                self, parent, "Glyph Proof Batch Wizard", "dialogs_trivialwizard"
            )
            self.subtitle.setText(
                "Choose a prefix and a line size, or paste JSON from Glyph Batch Recipe Settings. Use Next to review proof batches. Copy the result into a FontLab text workflow. Back retains your settings. The tool does not open tabs or change selection."
            )
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.extra_outputs: list[Any] = []
            self.status = g.QLabel("Ready. Preview uses the current font.")
            self.status.setWordWrap(True)
            self.pages = g.QStackedWidget()
            page = g.QWidget()
            form = g.QVBoxLayout(page)
            form.addWidget(g.QLabel("1. Choose glyphs and line size"))
            self.prefix = g.QLineEdit("")
            self.batch_size = g.QSpinBox()
            self.batch_size.setRange(1, 1000)
            self.batch_size.setValue(20)
            form.addWidget(g.QLabel("Name starts with (blank means all)"))
            form.addWidget(self.prefix)
            form.addWidget(g.QLabel("Glyphs per proof line"))
            form.addWidget(self.batch_size)
            form.addWidget(g.QLabel("Optional JSON from Glyph Batch Recipe Settings"))
            self.recipe_input = g.QPlainTextEdit()
            self.recipe_input.setPlaceholderText(
                "Paste a recipe, or leave blank to use the controls above."
            )
            form.addWidget(self.recipe_input)
            self.pages.addWidget(page)
            self.pages.addWidget(self.output)
            self.root.addWidget(self.pages)
            back = g.QPushButton("Back")
            next_button = g.QPushButton("Next: Review Proof")
            self.root.addWidget(back)
            self.root.addWidget(next_button)
            self._connect(back.clicked, lambda *a: self.pages.setCurrentIndex(0))
            self._connect(next_button.clicked, lambda *a: self.advance())
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
                names = tuple(n for n, _ in glyph_rows())
                payload = self.recipe_input.toPlainText().strip()
                if payload:
                    text, prefix, size = proof_from_recipe(payload, names)
                    self.prefix.setText(prefix)
                    self.batch_size.setValue(size)
                else:
                    text = proof_batches(names, self.prefix.text, self.batch_size.value)
                self.output.setPlainText(text)
                self.pages.setCurrentIndex(1)
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

        def advance(self) -> None:
            """Validate fresh inputs before moving to the review step."""
            if self.preview():
                self.pages.setCurrentIndex(1)

    return show_script_dialog(Dialog, "dialogs_trivialwizard")


if __name__ == "__main__":
    main()
