# this_file: Scripts/Dialogs/FontLab Script Scaffold Wizard.py
# SPDX-License-Identifier: Apache-2.0
"""Generate a small Python class which reads the current font.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Choose a class name and a title. Use Next to inspect valid Python source. Copy text from the preview into your own script; this tool writes no file.
Why: Generate code as text and quote user titles as data.
Benefit: Start a runnable font-reading script without editing a live font.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank classwizard dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
Archived replacements: Apache-2.0 owner grant. Upstream BSD headers and
collection GPL metadata have unresolved scope. No upstream code or assets copied.
The two archived variants consolidate into this FontLab-specific workflow;
original sample controls are not a claim of feature parity. Native acceptance pending.
Source: rescued/part2/ports/dialogs/pyqt-official/classwizard-035f3fbd2b81479a.py
SHA256: 1d69f1113b8c0a1eb508ee108639dea5bd114fd384ae132c3dd767efa45909fb
Source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/classwizard-035f3fbd2b81479a.py
SHA256: 93b55b89157b47b8676db5ce9e9a64641bf7d6290bc576f2c5af16079beef92d
"""

import keyword
from typing import Any


def scaffold(name: str, title: str) -> str:
    """Generate parseable Python. Treat titles as data and identifiers as syntax."""
    reserved = {"fl", "TITLE", "main", "tuple", "str", "ValueError", "print"}
    if not name.isidentifier() or keyword.iskeyword(name) or name in reserved:
        raise ValueError("Use a Python class identifier, such as AuditWidths.")
    return (
        "# this_file: My FontLab Tool.py\n"
        "from fly import fl\n\n"
        f"TITLE: str = {title!r}\n\n"
        f"class {name}:\n"
        "    title: str = TITLE\n\n"
        "    def glyph_names(self) -> tuple[str, ...]:\n"
        '        """Read current names without changing the font."""\n'
        "        font = fl.CurrentFont()\n"
        "        if font is None:\n"
        '            raise ValueError("Open a font first.")\n'
        "        return tuple(glyph.name for glyph in font.glyphs)\n\n"
        "def main() -> tuple[str, ...]:\n"
        '    """Return current-font names for use in your own tool."""\n'
        f"    return {name}().glyph_names()\n\n"
        'if __name__ == "__main__":\n'
        "    print(TITLE)\n"
        "    print(main())\n"
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
                "FontLab Script Scaffold Wizard",
                "dialogs_classwizard",
            )
            self.subtitle.setText(
                "Choose a class name and a title. Use Next to inspect valid Python source. Copy text from the preview into your own script; this tool writes no file."
            )
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.extra_outputs: list[Any] = []
            self.status = g.QLabel("Ready. Generate Python; no open font is required.")
            self.status.setWordWrap(True)
            self.pages = g.QStackedWidget()
            self.root.addWidget(self.pages)
            page = g.QWidget()
            form = g.QVBoxLayout(page)
            self.class_name = g.QLineEdit("MyFontTool")
            self.title_edit = g.QLineEdit("Inspect current font")
            form.addWidget(g.QLabel("Python class name"))
            form.addWidget(self.class_name)
            form.addWidget(g.QLabel("Tool title"))
            form.addWidget(self.title_edit)
            self.pages.addWidget(page)
            self.pages.addWidget(self.output)
            back = g.QPushButton("Back")
            next_button = g.QPushButton("Next: Review Python")
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
                text = scaffold(self.class_name.text, self.title_edit.text)
                self.output.setPlainText(text)
                self.status.setText(
                    "Python ready. Select and copy the code; no font was read."
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

    return show_script_dialog(Dialog, "dialogs_classwizard")


if __name__ == "__main__":
    main()
