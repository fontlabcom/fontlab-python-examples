# this_file: Scripts/Dialogs/Glyph Batch Recipe Settings.py
# SPDX-License-Identifier: Apache-2.0
"""Draft a JSON recipe from real glyph names.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Choose a prefix and a batch size on the settings pages. Preview captures the current font and builds a complete JSON recipe. Paste the JSON into Glyph Proof Batch Wizard to generate proof lines. No preferences are saved.
Why: Keep batch settings local and export an explicit glyph list.
Benefit: Reuse the recipe in Glyph Proof Batch Wizard without retyping settings.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank configdialog dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
The author supplies these first-party samples under Apache-2.0.
The Qt examples carry BSD headers and collection-level GPL metadata.
No code, helper or asset from these examples is included.
The two archived variants consolidate into this FontLab-specific workflow.
Historical source: rescued/part2/ports/dialogs/pyqt-official/configdialog-3f5f77c0358d9fef.py
SHA256: a8723ff0df166a67c564237dbf0c11dfe87d4f649b2769c2de409efc1508c33f
Historical source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/configdialog-3f5f77c0358d9fef.py
SHA256: 5ddbb490939e6e767b7603a197b0ec14019611ff4447c04fff97293593cb571d
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


def recipe(names: tuple[str, ...], prefix: str, size: int) -> str:
    """Return exact names and a reproducible batch plan; execute nothing."""
    if type(size) is not int or not 1 <= size <= 1000:
        raise ValueError("Batch size must be an integer from 1 to 1000.")
    chosen = [name for name in names if name.startswith(prefix)]
    if not chosen:
        raise ValueError("No glyph names match the prefix.")
    return json.dumps(
        {
            "prefix": prefix,
            "batch_size": size,
            "glyphs": chosen,
            "batches": (len(chosen) + size - 1) // size,
        },
        indent=2,
        ensure_ascii=False,
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
                self, parent, "Glyph Batch Recipe Settings", "dialogs_configdialog"
            )
            self.subtitle.setText(
                "Choose a prefix and a batch size on the settings pages. Preview captures the current font and builds a complete JSON recipe. Paste the JSON into Glyph Proof Batch Wizard to generate proof lines. No preferences are saved."
            )
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.extra_outputs: list[Any] = []
            self.status = g.QLabel("Ready. Preview uses the current font.")
            self.status.setWordWrap(True)
            self.navigation = g.QListWidget()
            self.navigation.addItems(["Glyph Scope", "Batch Size", "Recipe Preview"])
            self.pages = g.QStackedWidget()
            self.prefix = g.QLineEdit("")
            self.batch_size = g.QSpinBox()
            self.batch_size.setRange(1, 1000)
            self.batch_size.setValue(50)
            for label, control in (
                ("Name starts with (blank means all)", self.prefix),
                ("Glyphs per batch", self.batch_size),
            ):
                page = g.QWidget()
                layout = g.QVBoxLayout(page)
                layout.addWidget(g.QLabel(label))
                layout.addWidget(control)
                self.pages.addWidget(page)
            self.pages.addWidget(self.output)
            self.root.addWidget(self.navigation)
            self.root.addWidget(self.pages)
            self._connect(
                self.navigation.currentRowChanged,
                lambda index: self.pages.setCurrentIndex(index),
            )
            self.navigation.setCurrentRow(0)
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
                text = recipe(
                    tuple(n for n, _ in glyph_rows()),
                    self.prefix.text,
                    self.batch_size.value,
                )
                self.output.setPlainText(text)
                self.navigation.setCurrentRow(2)
                self.pages.setCurrentIndex(2)
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

    return show_script_dialog(Dialog, "dialogs_configdialog")


if __name__ == "__main__":
    main()
