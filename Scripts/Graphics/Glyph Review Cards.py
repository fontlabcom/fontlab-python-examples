# this_file: Scripts/Graphics/Glyph Review Cards.py
# SPDX-License-Identifier: Apache-2.0
"""What: Stage glyph review status and notes on a graphics canvas.
How: Embed one native form per matching glyph. Status and notes stay local.
Why: Review comments need a scratch space beside a font before handoff.
Usage: Enter a prefix that matches at most six names, then Refresh. Set each
status and note. Copy Result transfers the complete report to the clipboard.
Copy before Refresh or Close; Discard and Close explicitly drops local notes.
Benefit: Prepare a named review handoff without altering glyph notes or history.
Notes are plain text. Unsupported Qt text classes are refused during transfer.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt embeddeddialogs example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Historical source: rescued/part2/ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py
SHA256: c08d4c310c70b3a0e129085b79f59493472859819fdf1c75e7024345724a83bc
Historical source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py
SHA256: b90e385b1cb4ea7f2f202545920844cba59a825fcdf3986878ebd25d3fce1876
"""

TITLE = "Glyph Review Cards"
KEY = "graphics_embeddeddialogs"
HELP = "Keep up to six embedded glyph review forms. Copy notes before Refresh or Close."

from time import monotonic
from typing import Any


def check_names(names: tuple[str, ...]) -> tuple[str, ...]:
    """Refuse names that cannot survive plain-text proof transfer exactly."""
    if len(set(names)) != len(names):
        raise ValueError("Duplicate glyph names; refresh the font.")
    for name in names:
        if not name or any(
            c.isspace() or c == "/" or ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF
            for c in name
        ):
            raise ValueError("A glyph name cannot be transferred as exact slash text.")
    return names


def capture_names() -> tuple[str, ...]:
    """Use App's bounded double-read capture; never access native glyph caches."""
    import fly.ap.glyph_catalog as catalog

    deadline = monotonic() + 2.0
    names = check_names(
        tuple(row[0] for row in catalog.capture(deadline=deadline).rows)
    )
    if monotonic() >= deadline:
        raise TimeoutError("Glyph-name transfer expired; refresh again.")
    return names


def review_report(cards: tuple[tuple[str, str, str], ...]) -> str:
    """Serialize complete named reviews; preserve multiline text exactly."""
    paragraphs = []
    for name, status, note in cards:
        check_names((name,))
        if status not in ("Unreviewed", "Check", "OK"):
            raise ValueError("Unknown review status.")
        if any(c in note for c in ("\x00", "\u00a0", "\u2028", "\u2029", "\r")) or any(
            0xD800 <= ord(c) <= 0xDFFF for c in note
        ):
            raise ValueError("Review contains text that Qt cannot transfer exactly.")
        paragraphs.append(f"{name} [{status}]\n{note}")
    return "\n\n".join(paragraphs)


def panel_type(qt: Any) -> type:
    """Bind a modeless scene to the host Qt; retain and drain exact signals."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Keep state on a Python subclass; native scene items own no callbacks."""

        def __init__(self, parent: Any) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.Window)
            self.result = ""
            self.names: tuple[str, ...] = ()
            self.cards: list[tuple[str, Any, Any]] = []
            self.saved_review = ""
            self.discarding = False
            self.scope = signals.Scope(self.failure)
            self.terminal = signals.Scope(self.failure)
            self.terminal.connect(
                self.destroyed, lambda *args: self.destroyed_cleanup()
            )
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(760, 580)
            self.stack = gui.QVBoxLayout(self)
            self.stack.setContentsMargins(18, 18, 18, 18)
            self.message = gui.QLabel("Ready. Refresh reads the current font.", self)
            self.message.setTextFormat(core.Qt.PlainText)
            self.message.setWordWrap(True)
            intro = gui.QLabel(HELP, self)
            intro.setTextFormat(core.Qt.PlainText)
            intro.setWordWrap(True)
            self.stack.addWidget(intro)
            self.toolbar = gui.QHBoxLayout()
            self.stack.addLayout(self.toolbar)
            self.canvas = gui.QGraphicsScene(self)
            self.viewer = gui.QGraphicsView(self.canvas, self)
            self.stack.addWidget(self.viewer)
            self.output_box = gui.QPlainTextEdit(self)
            self.output_box.setReadOnly(True)
            self.stack.addWidget(self.output_box)
            self.stack.addWidget(self.message)
            self.build_controls()
            self.button("Refresh", self.refresh)
            self.button("Copy Result", self.copy_result)
            self.button("Close", self.close, closing=True)

        def failure(self, error: Exception) -> None:
            """Contain native callback errors and retain the panel for retry."""
            self.message.setText(str(error))

        def button(self, label: str, action: Any, *, closing: bool = False) -> Any:
            """Retain callbacks, including Close until failed disconnects clear."""
            control = gui.QPushButton(label, self)
            self.toolbar.addWidget(control)
            self.scope.connect(
                control.clicked, lambda *args: action(), closing=closing, retry=closing
            )
            return control

        def publish(self, text: str) -> None:
            """Publish only exact text; reject Qt normalization before enabling Copy."""
            self.output_box.setPlainText(text)
            if str(self.output_box.toPlainText()) != text:
                raise ValueError("Qt changed the result text; no copy is available.")
            self.result = text

        def clear_result(self) -> None:
            """Drop native item wrappers before scene.clear deletes their objects."""
            self.cards.clear()
            self.names, self.result = (), ""
            self.canvas.clear()
            self.output_box.setPlainText("")

        def refresh(self) -> bool:
            """Capture all input or clear stale scene and text on any failure."""
            if self.has_draft():
                self.message.setText(
                    "Copy review notes or Discard and Close before Refresh."
                )
                return False
            try:
                self.clear_result()
                self.names = capture_names()
                self.draw_scene()
                self.message.setText(
                    "Snapshot ready. Refresh after font changes; edits stay local."
                )
                return True
            except Exception as error:  # noqa: BLE001 - native UI boundary, including TimeoutError
                self.result = ""
                self.output_box.setPlainText("")
                try:
                    self.clear_result()
                except Exception as cleanup_error:  # noqa: BLE001 - retain failed scene ownership
                    self.failure(
                        RuntimeError(f"{error}; scene cleanup: {cleanup_error}")
                    )
                    return False
                self.failure(error)
                return False

        def copy_result(self) -> None:
            """Copy only a complete local result; never change a font or its history."""
            text = self.copy_payload()
            if not text:
                raise ValueError("Refresh to prepare a result before copying.")
            self.publish(text)
            gui.QApplication.clipboard().setText(text)
            self.saved_review = text
            self.message.setText(
                "Copied. Paste into the relevant FontLab text field or review file."
            )

        def destroyed_cleanup(self) -> None:
            """Release Python signal ownership after external parent destruction."""
            self.scope.finish(destroyed=True)
            self.terminal.finish(destroyed=True)
            self.release()

        def release(self) -> None:
            """Forget this window only if it still owns the host registry entry."""
            import sys

            registry = getattr(sys, "_fontlab_samples", {})
            if registry.get(KEY) is self:
                registry.pop(KEY)

        def closeEvent(self, event: Any) -> None:
            """Preserve drafts and refuse deletion when a signal cannot disconnect."""
            try:
                if self.has_draft():
                    self.message.setText(
                        "Unsaved review notes. Copy Result, or Discard and Close."
                    )
                    event.ignore()
                    return
                if not self.scope.finish() or not self.terminal.finish():
                    event.ignore()
                    return
                self.clear_result()
                self.release()
                event.accept()
                self.deleteLater()
            except Exception as error:  # noqa: BLE001 - native close boundary
                self.failure(error)
                event.ignore()

        def build_controls(self) -> None:
            """Keep a prefix filter and explicit discard action beside the cards."""
            self.prefix_entry = gui.QLineEdit(self)
            self.prefix_entry.setPlaceholderText("Glyph prefix (at most 6 matches)")
            self.toolbar.addWidget(self.prefix_entry)
            self.button("Discard and Close", self.discard, closing=True)

        def draw_scene(self) -> None:
            """Embed bounded plain-text forms; scene owns each proxy and its form."""
            prefix = str(properties.value(self.prefix_entry, "text"))
            names = tuple(name for name in self.names if name.startswith(prefix))
            if not names or len(names) > 6:
                raise ValueError("Choose a prefix with 1 to 6 matching glyphs.")
            for index, name in enumerate(names):
                form = gui.QWidget()
                column = gui.QVBoxLayout(form)
                label = gui.QLabel(name, form)
                label.setTextFormat(core.Qt.PlainText)
                column.addWidget(label)
                choice = gui.QComboBox(form)
                choice.addItems(["Unreviewed", "Check", "OK"])
                column.addWidget(choice)
                note = gui.QPlainTextEdit(form)
                note.setPlaceholderText("Local review note")
                column.addWidget(note)
                self.cards.append((name, choice, note))
                self.canvas.addWidget(form).setPos(
                    float(index % 2 * 300), float(index // 2 * 260)
                )
            self.saved_review = self.copy_payload()
            self.publish(self.saved_review)

        def copy_payload(self) -> str:
            """Read every card before transfer; reject a lossy plain-text value."""
            return review_report(
                tuple(
                    (
                        name,
                        str(properties.value(choice, "currentText")),
                        str(note.toPlainText()),
                    )
                    for name, choice, note in self.cards
                )
            )

        def has_draft(self) -> bool:
            """Preserve changed cards even when text cannot yet be serialized."""
            if self.discarding:
                return False
            try:
                return bool(self.cards) and self.copy_payload() != self.saved_review
            except (ValueError, RuntimeError, TimeoutError):
                return True

        def discard(self) -> None:
            """Drop editable local state only after an explicit discard action."""
            self.discarding = True
            try:
                self.close()
            finally:
                self.discarding = False

    return Panel


def main() -> Any:
    """Open through Fly and the host registry; never create an application."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import
    from fly import qt

    return scripting.show_script_dialog(panel_type(qt), KEY)


if __name__ == "__main__":
    main()
