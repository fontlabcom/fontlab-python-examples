# this_file: Scripts/Graphics/Glyph Mark Colour Board.py
# SPDX-License-Identifier: Apache-2.0
"""What: Drop colour swatches onto prefix-matched glyphs to set FontLab marks.
How: Capture current-font glyph identities. A drop makes one metadata Undo step
through App history. Read-back checks individually coloured layer overrides.
Native glyph-to-layer mark propagation is unverified.
Why: Organize a review group with visible glyph marks in the Font window.
Usage: Enter a glyph-name prefix, Refresh, then drag a swatch onto a tile.
Refresh after changing the font or master. None clears the glyph's mark.
Benefit: Flag individual glyphs directly without changing the font selection.
The table and selection swatches edit the same property; this board adds
prefix-scoped, drag-and-drop editing.
Glyphs with auto layers are refused. A partial write reports Edit > Undo.
Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; each drop edits one glyph.
Independent rewrite of the Qt dragdroprobot example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Source: rescued/part2/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py
SHA256: f1faf59693b2054c207de5811e7d721260755e6a5675f199f3472e3d520204d2
Source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py
SHA256: c021aba5ca45ca9cf3b0fde77ceb654ff5077191380d83cef5d84c1aec9c8313
"""

from time import monotonic
from typing import Any

TITLE = "Glyph Mark Colour Board"
KEY = "graphics_dragdroprobot"
# FontLab mark 0 is transparent; chromatic marks use HSL hue + 1.
SWATCHES = (
    ("None", 0, "transparent"),
    ("Red", 1, "#ff0000"),
    ("Yellow", 61, "#ffff00"),
    ("Green", 121, "#00ff00"),
    ("Cyan", 181, "#00ffff"),
    ("Blue", 241, "#0000ff"),
    ("Magenta", 301, "#ff00ff"),
)


def mark_from_colour(hue: int, saturation: int, alpha: int) -> int:
    """Accept only the board's six opaque hue colours or a transparent clear."""
    if alpha == 0:
        return 0
    if alpha != 255 or saturation != 255 or hue not in (0, 60, 120, 180, 240, 300):
        raise ValueError("Drop a mark-colour swatch from this board.")
    return hue + 1


def context_of(package: Any) -> tuple[int, int, str]:
    """Bind the workspace package, FontGate font and current master together."""
    if package is None or package.isNull:
        raise ValueError("Open a font, then Refresh the colour board.")
    return int(package.id), int(package.fgId), str(package.master)


def checked_glyph(
    context: tuple[int, int, str], identity: int | None, name: str
) -> tuple[Any, Any]:
    """Resolve only a current, valid glyph with the captured native identity."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import

    package = scripting.current_package()
    if context_of(package) != context:
        raise ValueError("The font or master changed; Refresh the colour board.")
    glyph = package.findName(name)
    if (
        glyph is None
        or glyph.isNull
        or not glyph.isValid
        or glyph.name != name
        or int(glyph.package.id) != context[0]
        or (identity is not None and int(glyph.id) != identity)
    ):
        raise ValueError("The glyph identity changed; Refresh the colour board.")
    return package, glyph


def board_snapshot(
    prefix: str,
) -> tuple[tuple[int, int, str], tuple[tuple[str, int, int], ...]]:
    """Capture immutable names, IDs and marks twice; never publish a partial board."""
    import fly.ap.glyph_catalog as catalog
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import

    deadline = monotonic() + 2.0
    context = context_of(scripting.current_package())
    names = tuple(
        row[0]
        for row in catalog.capture(deadline=deadline).rows
        if row[0].startswith(prefix)
    )
    if not names or len(names) > 100:
        raise ValueError("Choose a prefix with 1 to 100 matching glyphs.")

    def read() -> tuple[tuple[str, int, int], ...]:
        result = []
        for name in names:
            if monotonic() >= deadline:
                raise TimeoutError("Colour capture expired; Refresh again.")
            _, glyph = checked_glyph(context, None, name)
            result.append((name, int(glyph.id), int(glyph.mark or 0)))
        return tuple(result)

    first, second = read(), read()
    if first != second or context_of(scripting.current_package()) != context:
        raise ValueError("Glyph marks changed during capture; Refresh again.")
    if monotonic() >= deadline:
        raise TimeoutError("Colour capture expired; Refresh again.")
    return context, second


def apply_mark(
    context: tuple[int, int, str], identity: int, name: str, mark: int
) -> bool:
    """Set one glyph mark and check overrides without assuming propagation.

    Native propagation to layers that share the old glyph mark is unverified;
    accept either the old or new mark there. Reject changes to other marks.
    Enroll every layer and the glyph in one App metadata commit. Never
    notify an auto layer: history.commit owns the refusal before history starts.
    """
    import fly.ap.history as history  # noqa: PLR0402 - Fly requires module import

    if type(mark) is not int or mark not in {row[1] for row in SWATCHES}:
        raise ValueError("Unknown FontLab mark colour.")
    package, glyph = checked_glyph(context, identity, name)
    facts = history.scan_auto_facts(package)
    _, glyph = checked_glyph(context, identity, name)
    layers = tuple(glyph.layers)
    old_mark = int(glyph.mark or 0)
    before = tuple((int(layer.id), int(layer.mark or 0)) for layer in layers)
    if old_mark == mark:
        return False
    allowed = tuple(
        (lid, (value, mark) if value == old_mark else (value,)) for lid, value in before
    )

    def mutate() -> None:
        _, current = checked_glyph(context, identity, name)
        if (
            int(current.mark or 0) != old_mark
            or tuple((int(layer.id), int(layer.mark or 0)) for layer in current.layers)
            != before
        ):
            raise ValueError("Glyph marks changed before the drop; Refresh.")
        current.mark = mark

    def read_back() -> tuple[str, ...]:
        _, current = checked_glyph(context, identity, name)
        actual = tuple(
            (int(layer.id), int(layer.mark or 0)) for layer in current.layers
        )
        if (
            int(current.mark or 0) != mark
            or len(actual) != len(allowed)
            or any(
                actual_id != expected_id or value not in choices
                for (actual_id, value), (expected_id, choices) in zip(
                    actual, allowed, strict=True
                )
            )
        ):
            return (f"{name}: glyph or layer mark read-back differs from the drop.",)
        return ()

    result = history.commit(
        "Set Glyph Mark Colour",
        layers,
        (glyph,),
        mutate,
        operation="metadata",
        facts=facts,
        read_back=read_back,
    )
    if result.mismatches:
        raise history.PartialWriteError(
            "Set Glyph Mark Colour", [RuntimeError("; ".join(result.mismatches))]
        )
    return True


def panel_type(qt: Any) -> type:
    """Create a modeless colour-drop board; no native item stores Python state."""
    import fly.ap.draft_signals as signals
    import fly.ap.history as history  # noqa: PLR0402 - Fly requires module import
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Swatch(gui.QLabel):
        """Start a copy-only native colour drag from an owned label."""

        def __init__(self, owner: Any, name: str, css: str) -> None:
            gui.QLabel.__init__(self, name, owner)
            self.board_owner, self.swatch_css = owner, css
            self.setStyleSheet(
                f"background: {css}; border: 1px solid #808080; padding: 8px;"
            )
            self.setToolTip("Drag " + name + " onto a glyph tile")

        def mousePressEvent(self, event: Any) -> None:
            """Retain the board throughout Qt's nested drag event loop."""
            if event.button() != core.Qt.LeftButton or self.board_owner.busy:
                gui.QLabel.mousePressEvent(self, event)
                return
            drag = gui.QDrag(self)
            self.board_owner.busy = True
            try:
                mime = core.QMimeData()
                mime.setColorData(gui.QColor(self.swatch_css))
                drag.setMimeData(mime)
                drag.exec(core.Qt.CopyAction)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.board_owner.failure(error)
            finally:
                self.board_owner.busy = False
                drag.deleteLater()

    class Tile(gui.QLabel):
        """Route a colour drop to the exact captured glyph identity."""

        def __init__(self, owner: Any, name: str, identity: int, mark: int) -> None:
            gui.QLabel.__init__(self, name + f"\nMark {mark}")
            self.board_owner, self.glyph_name, self.glyph_identity = (
                owner,
                name,
                identity,
            )
            self.setTextFormat(core.Qt.PlainText)
            self.setAcceptDrops(True)
            self.setMinimumSize(150, 65)
            self.setStyleSheet("border: 1px solid #808080; padding: 8px;")

        def dropped_mark(self, event: Any) -> int:
            """Use explicit QColor conversion for Qt's QVariant colour payload."""
            if not self.board_owner.valid or not event.mimeData().hasColor():
                raise ValueError(
                    "Refresh, then drop a colour swatch onto a glyph tile."
                )
            colour = gui.QColor(event.mimeData().colorData())
            return mark_from_colour(
                int(colour.hslHue()), int(colour.hslSaturation()), int(colour.alpha())
            )

        def dragEnterEvent(self, event: Any) -> None:
            """Accept a supported colour only; contain all expected host refusals."""
            try:
                self.dropped_mark(event)
                event.setDropAction(core.Qt.CopyAction)
                event.accept()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.board_owner.failure(error)
                gui.QLabel.dragEnterEvent(self, event)
                event.ignore()

        def dragMoveEvent(self, event: Any) -> None:
            """Keep supported colours accepted while moving within a proxy tile."""
            try:
                self.dropped_mark(event)
                event.setDropAction(core.Qt.CopyAction)
                event.accept()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.board_owner.failure(error)
                gui.QLabel.dragMoveEvent(self, event)
                event.ignore()

        def dragLeaveEvent(self, event: Any) -> None:
            """Delegate leave cleanup explicitly to the native QLabel handler."""
            gui.QLabel.dragLeaveEvent(self, event)

        def dropEvent(self, event: Any) -> None:
            """One drop is one metadata action; partial failures keep the Undo hint."""
            try:
                mark = self.dropped_mark(event)
                changed = apply_mark(
                    self.board_owner.context_key,
                    self.glyph_identity,
                    self.glyph_name,
                    mark,
                )
                self.setText(self.glyph_name + f"\nMark {mark}")
                css = next(row[2] for row in SWATCHES if row[1] == mark)
                self.setStyleSheet(
                    f"background: {css}; border: 1px solid #808080; padding: 8px;"
                )
                self.board_owner.message.setText(
                    "Mark applied; one Edit > Undo step."
                    if changed
                    else "Mark already has that colour; no change."
                )
                event.setDropAction(core.Qt.CopyAction)
                event.accept()
            except (ValueError, RuntimeError, TimeoutError) as error:
                if isinstance(error, history.PartialWriteError):
                    self.board_owner.valid = False
                self.board_owner.failure(error)
                gui.QLabel.dropEvent(self, event)
                event.ignore()

    class Panel(gui.QWidget):
        """Own swatch drags, font binding, signal scope and safe scene teardown."""

        def __init__(self, parent: Any) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.Window)
            self.busy, self.valid = False, False
            self.context_key: tuple[int, int, str] = (0, 0, "")
            self.scope = signals.Scope(self.failure)
            self.terminal = signals.Scope(self.failure)
            self.swatches: list[Any] = []
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(760, 520)
            stack = gui.QVBoxLayout(self)
            self.message = gui.QLabel(
                "Enter a prefix, Refresh, then drag a swatch onto a glyph.", self
            )
            self.message.setTextFormat(core.Qt.PlainText)
            self.message.setWordWrap(True)
            stack.addWidget(self.message)
            swatch_row = gui.QHBoxLayout()
            stack.addLayout(swatch_row)
            for name, _, css in SWATCHES:
                swatch = Swatch(self, name, css)
                self.swatches.append(swatch)
                swatch_row.addWidget(swatch)
            controls = gui.QHBoxLayout()
            stack.addLayout(controls)
            self.prefix_entry = gui.QLineEdit(self)
            self.prefix_entry.setPlaceholderText(
                "Glyph-name prefix (at most 100 matches)"
            )
            controls.addWidget(self.prefix_entry)
            for label, action in (("Refresh", self.refresh), ("Close", self.close)):
                button = gui.QPushButton(label, self)
                controls.addWidget(button)
                self.scope.connect(
                    button.clicked,
                    lambda *args, action=action: action(),
                    closing=label == "Close",
                    retry=label == "Close",
                )
            self.canvas = gui.QGraphicsScene(self)
            stack.addWidget(gui.QGraphicsView(self.canvas, self))
            self.terminal.connect(self.destroyed, lambda *args: self.dispose(True))

        def failure(self, error: Exception) -> None:
            """Display the exact refusal or partial-write recovery text."""
            self.message.setText(str(error))

        def refresh(self) -> bool:
            """Refresh only outside a drag; clear stale glyph identities on failure."""
            if self.busy:
                self.message.setText("Finish the colour drag before Refresh.")
                return False
            self.valid = False
            self.canvas.clear()
            try:
                context, rows = board_snapshot(
                    str(properties.value(self.prefix_entry, "text"))
                )
                for index, (name, identity, mark) in enumerate(rows):
                    tile = Tile(self, name, identity, mark)
                    self.canvas.addWidget(tile).setPos(
                        float(index % 4 * 175), float(index // 4 * 100)
                    )
                self.context_key, self.valid = context, True
                self.message.setText(
                    f"{len(rows)} glyph tiles. Each changed drop is one metadata Undo step."
                )
                return True
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.canvas.clear()
                self.failure(error)
                return False

        def dispose(self, destroyed: bool = False) -> bool:
            """Drain signals before clearing scene objects; preserve failed Close."""
            if self.busy and not destroyed:
                self.message.setText("Finish the colour drag before Close.")
                return False
            if not self.scope.finish(destroyed=destroyed) or not self.terminal.finish(
                destroyed=destroyed
            ):
                return False
            self.valid = False
            if not destroyed:
                self.canvas.clear()
            import sys

            registry = getattr(sys, "_fontlab_samples", {})
            if registry.get(KEY) is self:
                registry.pop(KEY)
            return True

        def closeEvent(self, event: Any) -> None:
            """Refuse Close during a drag or failed disconnect, then defer deletion."""
            try:
                if not self.dispose():
                    event.ignore()
                    return
                event.accept()
                self.deleteLater()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.failure(error)
                event.ignore()

    return Panel


def main() -> Any:
    """Open in FontLab's application through the existing App window registry."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import
    from fly import qt

    return scripting.show_script_dialog(panel_type(qt), KEY)


if __name__ == "__main__":
    main()
