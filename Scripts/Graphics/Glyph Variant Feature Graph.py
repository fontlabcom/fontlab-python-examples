# this_file: Scripts/Graphics/Glyph Variant Feature Graph.py
# SPDX-License-Identifier: Apache-2.0
"""What: Show directed base-to-variant relationships for the current font.
How: Match an exact final suffix such as alt or ss01. Draw each base -> variant
pair and produce individual OpenType substitution statements in font order.
Why: A feature draft is easier to review when its name relationships are visible.
Usage: Enter a suffix without the dot, Refresh, then Copy Result. Paste the
statements into a chosen feature in FontLab and compile there after review.
Benefit: Inspect proposed substitutions before use.
The graph infers names only; it does not read, validate or compile feature code.
The full text draft is retained; the scene shows at most 100 pairs.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt diagramscene example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Historical source: rescued/part2/ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py
SHA256: 9a955af5875f27bba1baad27d5c508910c80a5ec6463d7cb00890e983322fe56
Historical source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py
SHA256: 2f1d99279f78a43459928e59388681eb4ded7a85f0bd7b3cb6a7593980d05f1e
"""

TITLE = "Glyph Variant Feature Graph"
KEY = "graphics_diagramscene"
HELP = (
    "Map exact suffix variants and copy a substitution draft; no features are changed."
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


def variant_edges(names: tuple[str, ...], suffix: str) -> tuple[tuple[str, str], ...]:
    """Resolve exact terminal suffixes; do not infer a missing base glyph."""
    import re

    if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", suffix) is None:
        raise ValueError("Enter an ASCII suffix without a dot, for example ss01.")
    known = set(check_names(names))
    ending = "." + suffix
    edges = tuple(
        (name[: -len(ending)], name)
        for name in names
        if name.endswith(ending) and name[: -len(ending)] in known
    )
    if not edges:
        raise ValueError(
            "No matching base/variant pairs. Orphan variants have no base."
        )
    return edges


def feature_draft(edges: tuple[tuple[str, str], ...]) -> str:
    """Use escaped feature names; refuse names outside the feature-name grammar."""
    import re

    statements = ["# Draft only; choose a feature and compile in FontLab."]
    for base, variant in edges:
        if any(
            re.fullmatch(r"[A-Za-z_][A-Za-z_0-9.*+:^|~\-]{0,62}", n) is None
            and n != ".notdef"
            for n in (base, variant)
        ):
            raise ValueError(
                "A glyph name cannot be emitted as an OpenType feature name."
            )
        # Escape every name, including feature-language keywords.
        left, right = "\\" + base, "\\" + variant
        statements.append(f"sub {left} by {right};")
    return "\n".join(statements)


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
            self.names, self.result = (), ""
            self.canvas.clear()
            self.output_box.setPlainText("")

        def refresh(self) -> bool:
            """Capture all input or clear stale scene and text on any failure."""
            try:
                self.clear_result()
                self.names = capture_names()
                self.draw_scene()
                self.message.setText(
                    self.scene_summary + " Refresh after font changes."
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
            """Refuse deletion when an owned signal cannot disconnect."""
            try:
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
            """Keep one exact suffix field; graph coordinates stay local."""
            self.suffix_entry = gui.QLineEdit(self)
            self.suffix_entry.setText("alt")
            self.suffix_entry.setToolTip("Final glyph suffix, without its dot")
            self.toolbar.addWidget(self.suffix_entry)

        def draw_scene(self) -> None:
            """Draw a clear directed edge for each pair; retain full names in text."""
            edges = variant_edges(
                self.names, str(properties.value(self.suffix_entry, "text"))
            )
            draft = feature_draft(edges)
            for index, (base, variant) in enumerate(edges[:100]):
                y = float(index * 48)
                self.canvas.addSimpleText(base).setPos(0.0, y)
                self.canvas.addSimpleText(variant).setPos(320.0, y)
                self.canvas.addLine(210.0, y + 14.0, 300.0, y + 14.0)
                self.canvas.addLine(300.0, y + 14.0, 290.0, y + 9.0)
                self.canvas.addLine(300.0, y + 14.0, 290.0, y + 19.0)
            # Scroll instead of shrinking large graphs to unreadable text.
            self.canvas.setSceneRect(self.canvas.itemsBoundingRect())
            self.publish(draft)
            self.scene_summary = f"First {min(100, len(edges))} of {len(edges)} pairs shown; full draft available."
            self.message.setText(self.scene_summary)

    return Panel


def main() -> Any:
    """Open through Fly and the host registry; never create an application."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import
    from fly import qt

    return scripting.show_script_dialog(panel_type(qt), KEY)


if __name__ == "__main__":
    main()
