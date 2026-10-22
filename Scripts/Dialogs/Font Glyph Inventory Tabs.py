# this_file: Scripts/Dialogs/Font Glyph Inventory Tabs.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect glyph counts, names and Unicode assignments in three tabs.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Click Preview after font changes. General gives exact counts, Names keeps font order, and Unicode groups all assigned glyph names. Select and copy text from any tab.
Why: Separate summary, names and Unicode into read-only tabs.
Benefit: Copy a complete font inventory without changing glyph metadata.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank tabdialog dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
Archived replacements: Apache-2.0, own earlier work. Upstream BSD headers and
collection GPL metadata have unresolved scope. No upstream code or assets copied.
The two archived variants consolidate into this FontLab-specific workflow;
original sample controls are not a claim of feature parity. Native acceptance pending.
Historical source: rescued/part2/ports/dialogs/pyqt-official/tabdialog-dab5fd4c94ec518d.py
SHA256: f0429bb770550780ba27dd2def628e0189a5665595501f32dfb1ebf9ef98c7c0
Historical source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/tabdialog-dab5fd4c94ec518d.py
SHA256: 6fd6f74eddf5d3579fc8b46e70fab7de6444cd70d41a2776c1ca437b345fc2bf
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


def inventory(rows: tuple[tuple[str, tuple[int, ...]], ...]) -> tuple[str, str, str]:
    """Return three plain-text pages. Preserve duplicate codepoint assignments."""
    mapping: dict[int, list[str]] = {}
    for name, codes in rows:
        for code in dict.fromkeys(codes):
            mapping.setdefault(code, []).append(name)
    summary = (
        f"Glyphs: {len(rows)}\nEncoded glyphs: {sum(bool(c) for _, c in rows)}"
        f"\nDistinct codepoints: {len(mapping)}"
    )
    return (
        summary,
        "\n".join(n for n, _ in rows),
        "\n".join(f"U+{c:04X}  " + ", ".join(mapping[c]) for c in sorted(mapping)),
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
                self, parent, "Font Glyph Inventory Tabs", "dialogs_tabdialog"
            )
            self.subtitle.setText(
                "Click Preview after font changes. General gives exact counts, Names keeps font order, and Unicode groups all assigned glyph names. Select and copy text from any tab."
            )
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.extra_outputs: list[Any] = []
            self.status = g.QLabel("Ready. Preview uses the current font.")
            self.status.setWordWrap(True)
            self.tabs = g.QTabWidget()
            self.extra_outputs = [g.QPlainTextEdit(), g.QPlainTextEdit()]
            for title, editor in zip(
                ("General", "Names", "Unicode"), [self.output, *self.extra_outputs]
            ):
                editor.setReadOnly(True)
                self.tabs.addTab(editor, title)
            self.root.addWidget(self.tabs)
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
                text, names, codes = inventory(glyph_rows())
                self.extra_outputs[0].setPlainText(names)
                self.extra_outputs[1].setPlainText(codes)
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

    return show_script_dialog(Dialog, "dialogs_tabdialog")


if __name__ == "__main__":
    main()
