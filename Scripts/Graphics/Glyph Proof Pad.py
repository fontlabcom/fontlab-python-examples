# this_file: Scripts/Graphics/Glyph Proof Pad.py
# SPDX-License-Identifier: Apache-2.0
"""What: Browse the current font as a nine-cell proof-name pad.
How: Capture glyph names once. Previous and Next change the page. Click a
named cell to prepare its exact slash name; Copy Result transfers the text.
Why: Unencoded glyphs also need reliable proof-text access.
Usage: Enter a glyph-name prefix, then Refresh after font changes. Use Previous/Next (Alt+Left/Alt+Right),
click a cell, then Copy Result and paste in a Glyph window text bar.
Benefit: Build proof input without changing the Font window selection.
Only current-font names appear; the UI does not use system-font substitutes.
The original OpenGL viewport and animation are replaced by plain Qt widgets.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt padnavigator example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Source: rescued/part2/ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py
SHA256: 66f7c5169c23e0adb6a7cb76b9fdffbf33b27af79bc987cafb8534365d70632d
Source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py
SHA256: f6af280b00f13384566780930eb7aa33b57c5202a933315841d946fcf79cfe07
"""

TITLE = "Glyph Proof Pad"
KEY = "graphics_padnavigator"
HELP = (
    "Browse nine current-font names at a time. Click a tile to prepare its slash name."
)

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


def page_names(names: tuple[str, ...], index: int) -> tuple[str, ...]:
    """Return exactly one nine-name page; refuse empty or out-of-range input."""
    check_names(names)
    if not names:
        raise ValueError("The font is empty.")
    if type(index) is not int or not 0 <= index < (len(names) + 8) // 9:
        raise ValueError("Page is outside the captured font.")
    return names[index * 9 : (index + 1) * 9]


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
            self.page_index = 0
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

        def refresh(self) -> bool:
            """Capture all input or clear stale scene and text on any failure."""
            try:
                self.clear_result()
                prefix = str(properties.value(self.prefix_entry, "text"))
                self.names = tuple(
                    name for name in capture_names() if name.startswith(prefix)
                )
                self.page_index = 0
                self.draw_scene()
                self.message.setText(
                    "Read-only snapshot ready. Refresh after font changes."
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
            self.message.setText(
                "Copied. Paste into the relevant FontLab text field or review file."
            )

        def copy_payload(self) -> str:
            """Return the captured plain-text result."""
            return self.result

        def release(self) -> None:
            """Forget this window only if it still owns the host registry entry."""
            import sys

            registry = getattr(sys, "_fontlab_samples", {})
            if registry.get(KEY) is self:
                registry.pop(KEY)

        def build_controls(self) -> None:
            """Keep page movement explicit; shortcuts are active in this panel."""
            self.page_scope = signals.Scope(self.failure)
            self.prefix_entry = gui.QLineEdit(self)
            self.prefix_entry.setPlaceholderText("Glyph-name prefix")
            self.toolbar.addWidget(self.prefix_entry)
            self.button("Previous", lambda: self.navigate(-1)).setShortcut(
                gui.QKeySequence("Alt+Left")
            )
            self.button("Next", lambda: self.navigate(1)).setShortcut(
                gui.QKeySequence("Alt+Right")
            )

        def clear_result(self) -> None:
            """Disconnect page controls before their embedded widgets are deleted."""
            self.result = ""
            self.output_box.setPlainText("")
            if not self.page_scope.finish():
                raise RuntimeError("Cannot release the previous page; retry Close.")
            self.page_scope = signals.Scope(self.failure)
            self.clear_base()

        def clear_base(self) -> None:
            """Remove scene contents after page callbacks are disconnected."""
            self.names, self.result = (), ""
            self.canvas.clear()
            self.output_box.setPlainText("")

        def navigate(self, amount: int) -> None:
            """Clamp movement within the snapshot; never recapture on navigation."""
            if not self.names:
                raise ValueError("Refresh the current font first.")
            previous = self.page_index
            self.page_index = max(
                0, min((len(self.names) - 1) // 9, self.page_index + amount)
            )
            try:
                self.draw_scene()
            except Exception:
                self.page_index = previous
                self.result = ""
                self.output_box.setPlainText("")
                raise

        def choose(self, name: str) -> None:
            """Prepare one exact current-page name without touching selection."""
            if name not in page_names(self.names, self.page_index):
                raise ValueError("Choose a glyph on the current page.")
            self.publish("/" + name)

        def draw_scene(self) -> None:
            """Release the old page, then embed nine or fewer native buttons."""
            names = page_names(self.names, self.page_index)
            if not self.page_scope.finish():
                raise RuntimeError("Cannot release the previous page; retry Close.")
            self.canvas.clear()
            self.page_scope = signals.Scope(self.failure)
            for index, name in enumerate(names):
                tile = gui.QPushButton(name.replace("&", "&&"))
                tile.setToolTip(name)
                self.page_scope.connect(
                    tile.clicked, lambda *args, name=name: self.choose(name)
                )
                self.canvas.addWidget(tile).setPos(
                    float(index % 3 * 200), float(index // 3 * 70)
                )
            self.publish("".join("/" + name for name in names))
            self.message.setText(
                f"Page {self.page_index + 1} / {(len(self.names) + 8) // 9}. Click a name, then Copy Result."
            )

        def closeEvent(self, event: Any) -> None:
            """Drain page signals before the main panel lifetime ends."""
            try:
                if not self.page_scope.finish():
                    event.ignore()
                    return
                if not self.scope.finish() or not self.terminal.finish():
                    event.ignore()
                    return
                self.clear_base()
                self.release()
                event.accept()
                self.deleteLater()
            except Exception as error:  # noqa: BLE001 - native close boundary
                self.failure(error)
                event.ignore()

        def destroyed_cleanup(self) -> None:
            """Forget page emitters after parent destruction without native calls."""
            self.page_scope.finish(destroyed=True)
            self.scope.finish(destroyed=True)
            self.terminal.finish(destroyed=True)
            self.release()

    return Panel


def main() -> Any:
    """Open through Fly and the host registry; never create an application."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import
    from fly import qt

    return scripting.show_script_dialog(panel_type(qt), KEY)


if __name__ == "__main__":
    main()
