# this_file: Scripts/Graphics/Glyph Proof Layout.py
# SPDX-License-Identifier: Apache-2.0
"""What: Compare current-master advance widths and geometric side bearings.
How: Read a prefix-matched sample twice and build an anchored spacing strip.
Each tile's width is proportional to its advance. Hover for full measurements;
zero advances use a vertical marker and a separate measurement label.
Why: Compare relative widths at a glance while reviewing spacing in FontLab.
Usage: Open a font, enter a prefix with at most twelve matches, set the strip
width, then Refresh. Copy Result sends slash names to a Glyph window text bar.
Benefit: Spot width outliers without changing outlines or font metrics.
Empty layers have no ink margins; their side bearings show an em dash.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt anchorlayout example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Source: rescued/part2/ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py
SHA256: 4de40f5bc168015793f3529ef70f2e69dc46be41b38d17afb29f7e34ef8d717f
Source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py
SHA256: 60caa0dacfd8b8e41a4c8a5c83e5aced63a298e574433410c25e529452560ad2
"""

TITLE = "Glyph Proof Layout"
KEY = "graphics_anchorlayout"
HELP = (
    "Compare current-master widths and side bearings. Tiles have proportional advances."
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


def proof_sample(names: tuple[str, ...], prefix: str) -> tuple[str, ...]:
    """Keep font order; refuse excess results rather than silently truncating."""
    selected = tuple(name for name in check_names(names) if name.startswith(prefix))
    if not selected:
        raise ValueError("No glyph names match this prefix.")
    if len(selected) > 12:
        raise ValueError("More than 12 matches. Enter a narrower prefix.")
    return selected


def strip_widths(advances: tuple[float, ...], width: float) -> tuple[float, ...]:
    """Scale nonnegative advances exactly; a zero advance has zero strip width."""
    from math import isfinite

    if not isfinite(width) or width <= 0 or not advances:
        raise ValueError("Choose a positive strip width and a nonempty sample.")
    if any(not isfinite(a) or a < 0 for a in advances) or sum(advances) <= 0:
        raise ValueError(
            "Advances must be finite, nonnegative and have a positive total."
        )
    return tuple(width * advance / sum(advances) for advance in advances)


def capture_spacing(
    names: tuple[str, ...],
) -> tuple[tuple[str, float, float | None, float | None], ...]:
    """Double-read owned current-master layers without changing native objects.

    App's catalogue supplies names; this bounded adapter reads only the named
    layers because the public spacing capture targets selection, not prefixes.
    Glyph, layer and package identities, master and values must remain equal.
    """
    from math import isfinite

    import fly.ap.qt_properties as properties
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module imports

    deadline = monotonic() + 2.0

    def read() -> tuple:
        package = scripting.current_package()
        if package is None:
            raise ValueError("Open a font, then Refresh.")
        context = (int(package.id), int(package.fgId), str(package.master))
        rows, identities = [], []
        for name in names:
            if monotonic() >= deadline:
                raise TimeoutError("Spacing capture expired; no partial strip.")
            glyph = package.findName(name)
            if (
                glyph is None
                or glyph.isNull
                or not glyph.isValid
                or int(glyph.package.id) != context[0]
                or glyph.name != name
            ):
                raise ValueError("A glyph changed or belongs to another font; Refresh.")
            layer = glyph.findLayer(context[2])
            if layer is None or layer.isNull:
                raise ValueError("A current-master layer is missing; Refresh.")
            advance = float(layer.advanceWidth)
            left = right = None
            if int(properties.value(layer, "shapesCount")):
                box = properties.value(layer, "boundingBox")
                if not properties.value(box, "isNull"):
                    left = float(properties.value(box, "left"))
                    right = advance - float(properties.value(box, "right"))
            if any(v is not None and not isfinite(v) for v in (advance, left, right)):
                raise ValueError("Spacing measurements must be finite.")
            identities.append((int(glyph.id), int(layer.id)))
            rows.append((name, advance, left, right))
        return context, tuple(identities), tuple(rows)

    first, second = read(), read()
    package = scripting.current_package()
    final = (
        None
        if package is None
        else (int(package.id), int(package.fgId), str(package.master))
    )
    if monotonic() >= deadline:
        raise TimeoutError("Spacing capture expired; no partial strip.")
    if first != second or second[0] != final:
        raise ValueError("Font, master or spacing changed; Refresh.")
    return second[2]


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
            """Keep a prefix and explicit layout width beside Refresh."""
            self.prefix_entry = gui.QLineEdit(self)
            self.prefix_entry.setPlaceholderText("Glyph prefix (at most 12 matches)")
            self.toolbar.addWidget(self.prefix_entry)
            self.width_control = gui.QSpinBox(self)
            self.width_control.setRange(320, 2400)
            self.width_control.setValue(900)
            self.width_control.setToolTip("Layout width in scene units")
            self.toolbar.addWidget(self.width_control)

        def draw_scene(self) -> None:
            """Anchor each tile top/bottom and join consecutive left/right edges."""
            names = proof_sample(
                self.names, str(properties.value(self.prefix_entry, "text"))
            )
            width = int(properties.value(self.width_control, "value"))
            rows = capture_spacing(names)
            sizes = strip_widths(tuple(row[1] for row in rows), float(width))
            container = gui.QGraphicsWidget()
            anchors = gui.QGraphicsAnchorLayout()
            anchors.setSpacing(0.0)
            anchors.setContentsMargins(0.0, 0.0, 0.0, 0.0)
            previous, x = None, 0.0
            for index, ((name, advance, left, right), size) in enumerate(
                zip(rows, sizes, strict=True)
            ):
                lsb = "—" if left is None else f"{left:g}"
                rsb = "—" if right is None else f"{right:g}"
                measurements = f"{name}\nAdvance {advance:g}\nLSB {lsb}  RSB {rsb}"
                label = gui.QLabel(measurements)
                label.setTextFormat(core.Qt.PlainText)
                label.setStyleSheet("border: 1px solid #8596a0; padding: 4px;")
                proxy = self.canvas.addWidget(label)
                proxy.setToolTip(measurements)
                proxy.setMinimumSize(size, 120.0)
                proxy.setPreferredSize(size, 120.0)
                proxy.setMaximumSize(size, 120.0)
                anchors.addAnchor(anchors, core.Qt.AnchorTop, proxy, core.Qt.AnchorTop)
                anchors.addAnchor(
                    proxy, core.Qt.AnchorBottom, anchors, core.Qt.AnchorBottom
                )
                anchors.addAnchor(
                    previous if previous is not None else anchors,
                    core.Qt.AnchorRight if previous is not None else core.Qt.AnchorLeft,
                    proxy,
                    core.Qt.AnchorLeft,
                )
                if size == 0.0:
                    self.canvas.addLine(x, 0.0, x, 120.0)
                # Full numeric captions stay readable even for very narrow/zero tiles.
                self.canvas.addSimpleText(measurements.replace("\n", "  ")).setPos(
                    0.0, 140.0 + index * 24.0
                )
                x += size
                previous = proxy
            anchors.addAnchor(
                previous, core.Qt.AnchorRight, anchors, core.Qt.AnchorRight
            )
            container.setLayout(anchors)
            self.canvas.addItem(container)
            container.setGeometry(core.QRectF(0.0, 0.0, float(width), 120.0))
            self.canvas.setSceneRect(self.canvas.itemsBoundingRect())
            self.publish("".join("/" + name for name in names))

    return Panel


def main() -> Any:
    """Open through Fly and the host registry; never create an application."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import
    from fly import qt

    return scripting.show_script_dialog(panel_type(qt), KEY)


if __name__ == "__main__":
    main()
