# this_file: Scripts/Widgets/Script Icon Browser.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/icons-505d60a757bbc177.py
# preserved-source-sha256: cc6a383aa61e4cd0cce357e12e275ff643bd866ad3e1695254d3216d9ed104b7
# preserved-source: rescued/part2/ports/widgets/pyqt-official/icons-505d60a757bbc177.py
# preserved-source-sha256: 68749115c6766e274fc7114a18ab9ef26a1cd0434241b6abab5ddb6eeed00010
"""What: Browse the standard icons supplied by FontLab's current Qt style.
How: Enumerate QStyle SP_ constants, filter their names and show each icon
beside its enum name. A selected row produces pasteable PythonQt code.
Why: Use icons already supplied by the host instead of bundling image assets.
Usage: Filter by a name such as Dialog or Dir. Preview, then select an icon.
Copy the code below into a FontLab script. These are Qt standard icons;
FontLab's private resource icons are outside this browser.
Benefit: Build consistent script panels without external icon dependencies.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Icons example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.
"""

from typing import Any


def icon_names(style_type: type, query: str) -> tuple[str, ...]:
    """List enum names only. Never read arbitrary native object properties."""
    return tuple(
        name
        for name in sorted(dir(style_type))
        if name.startswith("SP_")
        and name != "SP_CustomBase"
        and query.casefold() in name.casefold()
    )


def main() -> Any:
    """Open the owned modeless App panel. Import Qt only in the host."""
    import fly.ap.qt_properties as properties
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module imports
    from fly import qt

    g = qt.QtGui
    base = scripting.names_dialog_type()

    class Dialog(base):
        """Browse host icons and prepare receiver-specific code for a panel method."""

        def __init__(self, parent: Any) -> None:
            """Build labelled controls with a selectable plain-text result."""
            base.__init__(
                self, parent, "Script Icon Browser", "widgets_script_icon_browser"
            )
            self.subtitle.setText(
                "Browse host-style Qt icons. Select a result for PythonQt code."
            )
            self.filter_text = g.QLineEdit()
            self.filter_text.setPlaceholderText("Icon name contains (optional)")
            self.icons = g.QListWidget()
            self.enum_names: tuple[str, ...] = ()
            self.root.addWidget(self.filter_text)
            self.root.addWidget(self.icons)
            self._connect(
                self.icons.currentRowChanged, lambda row: self.select_icon(int(row))
            )
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.status = g.QLabel(
                "Filter host-style icons, then Preview and select a row."
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
            """Refresh available host-style icons; clear failed icon results."""
            self.status.setText("Reading host-style icons...")
            self.output.setPlainText("")
            try:
                self.build_result()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output.setPlainText("")
                self.enum_names = ()
                self.icons.clear()
                self.status.setText(str(error))

        def build_result(self) -> None:
            """Build one complete result from current controls and context."""
            self.enum_names = ()
            self.icons.clear()
            self.enum_names = icon_names(
                g.QStyle, str(properties.value(self.filter_text, "text"))
            )
            style = self.style()
            for name in self.enum_names:
                item = g.QListWidgetItem(name)
                item.setIcon(style.standardIcon(getattr(g.QStyle, name)))
                self.icons.addItem(item)
            self.status.setText(
                f"{len(self.enum_names)} standard icons. Select a row to get code."
            )

        def select_icon(self, row: int) -> None:
            """Read Python-side row state; native item wrappers keep no custom data."""
            self.output.setPlainText("")
            try:
                if 0 <= row < len(self.enum_names):
                    self.publish(
                        "# Inside a FontLab panel method; self is the panel.\n"
                        "from fly import qt\n"
                        + f"icon = self.style().standardIcon(qt.QtGui.QStyle.{self.enum_names[row]})\n"
                    )
                    self.status.setText("Icon code ready. Select text and Copy.")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output.setPlainText("")
                self.status.setText(str(error))

    return scripting.show_script_dialog(Dialog, "widgets_script_icon_browser")


if __name__ == "__main__":
    main()
