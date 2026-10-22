# this_file: Scripts/Tools/Pair Proof Generator.py
# SPDX-License-Identifier: Apache-2.0
"""What: Generate current-font glyph pairs from two explicit name lists.
How: Combine all left/right names, or zip equal-length lists. Apply each side's
suffix, then validate every resulting name against the current font.
Why: Cartesian combinations expose spacing relationships absent from an
adjacent-pair proof. Unencoded alternates remain usable through slash names.
Usage: Enter space-separated names without slashes. Choose Product or Zip.
Optional fillers are name lists. Copy Fresh Result to a Glyph window text bar.
Benefit: Prepare every requested pair in stable order without editing kerning.
This tool generates proofs. Use File > Export > Metrics for AFM kerning output
and scriptmix Kerning > Classes Browser for class inspection.
scriptmix Kerning > Missing Pairs also builds Cartesian combinations, filtered
to missing kerning. This tool keeps all pairs and adds Zip, suffixes and fillers.
It does not extract existing-kerning proof strings or export KRN, Unicode
strings or OpenType class declarations.

Independent behaviour-only rewrite of the pair-generation idea from Pairs.py.
Credit: Vassil Kateliev and Karandash Type Foundry; kateliev/TypeRig, MPL-2.0.
No TypeRig code, comments, icons or resources are included.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.
"""

from itertools import product
from typing import Any

TITLE = "Pair Proof Generator"
HELP = (
    "Generate all combinations or zip equal lists. Copy slash proof lines to FontLab."
)
FIELDS = (
    ("Left names", "A"),
    ("Right names", "V"),
    ("Left suffix", ""),
    ("Right suffix", ""),
    ("Mode: Product or Zip", "Product"),
    ("Left filler names", ""),
    ("Right filler names", ""),
)
CHOICES: dict[int, tuple[str, ...]] = {4: ("Product", "Zip")}
_PANELS: list[Any] = []


def resolve(text: str, suffix: str, known: set[str]) -> tuple[str, ...]:
    """Validate complete name lists before any output is built."""
    checked(text)
    checked(suffix)
    names = tuple(name + suffix for name in text.split())
    for name in names:
        if name not in known or "/" in name or any(char.isspace() for char in name):
            raise ValueError(f"Unknown or unusable glyph name: {name!r}")
    return names


def build_output(fields: tuple[str, ...]) -> str:
    """Retain input order and repeats in a complete validated pair product."""
    import fly.ap.glyph_catalog as catalog

    left_text, right_text, left_suffix, right_suffix, mode, before, after = fields
    known = {row[0] for row in catalog.capture().rows}
    left = resolve(left_text, left_suffix, known)
    right = resolve(right_text, right_suffix, known)
    prefix, suffix = resolve(before, "", known), resolve(after, "", known)
    if not left or not right:
        raise ValueError("Enter at least one glyph on both sides.")
    if mode == "Product":
        pairs = product(left, right)
    elif mode == "Zip":
        if len(left) != len(right):
            raise ValueError("Zip requires equal-length lists.")
        pairs = zip(left, right, strict=True)
    else:
        raise ValueError("Mode must be Product or Zip.")
    return "\n".join(
        "".join("/" + name for name in (*prefix, a, b, *suffix)) for a, b in pairs
    )


def checked(text: str) -> str:
    """Refuse characters that the Qt bridge or proof syntax can change."""
    if any(char in text for char in ("\0", "\u00a0", "\u2028", "\u2029", "\r")):
        raise ValueError("Text contains NUL, NBSP, CR or a Unicode line separator.")
    try:
        text.encode("utf-8")
    except UnicodeError as error:
        raise ValueError("Text contains an invalid Unicode surrogate.") from error
    return text


def show(qt: Any, parent: Any) -> Any:
    """Open an owned modeless panel; drain callbacks before deletion."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own inputs, current output and a retryable signal scope."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(740, 540)
            self.stack_box = gui.QVBoxLayout(self)
            self.status_line = gui.QLabel(HELP, self)
            self.stack_box.addWidget(self.status_line)
            self.signal_scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )

        def build_controls(self) -> None:
            """Build fallible controls under the outer owned-window cleanup guard."""
            self.input_boxes: list[Any] = []
            for index, (label, initial) in enumerate(FIELDS):
                self.stack_box.addWidget(gui.QLabel(label, self))
                if index in CHOICES:
                    item = gui.QComboBox(self)
                    item.addItems(list(CHOICES[index]))
                    item.setCurrentIndex(CHOICES[index].index(initial))
                else:
                    item = gui.QLineEdit(self)
                    item.setText(initial)
                self.stack_box.addWidget(item)
                self.input_boxes.append(item)
            self.output_box = gui.QPlainTextEdit(self)
            self.output_box.setReadOnly(True)
            self.stack_box.addWidget(self.output_box)
            for label, action in (
                ("Refresh Result", self.refresh_output),
                ("Copy Fresh Result", self.copy_output),
            ):
                button = gui.QPushButton(label, self)
                self.stack_box.addWidget(button)
                self.signal_scope.connect(
                    button.clicked, lambda *args, call=action: call()
                )
            self.signal_scope.connect(
                self.destroyed, lambda *args: self.release_owner()
            )

        def fresh_output(self) -> str:
            """Recapture live input; never export a previous font's result."""
            fields = tuple(
                checked(
                    str(
                        properties.value(
                            item, "currentText" if index in CHOICES else "text"
                        )
                    )
                )
                for index, item in enumerate(self.input_boxes)
            )
            return checked(build_output(fields))

        def refresh_output(self) -> None:
            """Replace the result atomically; clear stale output after a refusal."""
            try:
                text = self.fresh_output()
                self.output_box.setPlainText(text)
                self.status_line.setText("Result refreshed. " + HELP)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output_box.setPlainText("")
                self.status_line.setText(str(error))

        def copy_output(self) -> None:
            """Read again before copying a FontLab-consumable proof or table."""
            try:
                text = self.fresh_output()
                if not text:
                    raise ValueError("No matching output to copy.")
                gui.QApplication.clipboard().setText(text)
                self.output_box.setPlainText(text)
                self.status_line.setText("Fresh result copied.")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output_box.setPlainText("")
                self.status_line.setText(str(error))

        def release_owner(self) -> None:
            """Release Python state when the native parent destroys this panel."""
            self.signal_scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Retain failed disconnections for a window-Close retry."""
            if not self.signal_scope.finish():
                event.ignore()
                return
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.build_controls()
        panel.refresh_output()
        panel.show()
    except Exception:
        if panel.signal_scope.finish():
            _PANELS.remove(panel)
            panel.deleteLater()
        raise
    return panel


def main() -> None:
    """Open inside FontLab's existing application and main window."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
