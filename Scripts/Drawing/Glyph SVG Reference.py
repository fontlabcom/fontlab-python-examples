# this_file: Scripts/Drawing/Glyph SVG Reference.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source: rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py
# preserved-source-sha256: d2ccb421fa24dcc962e4abda1d081a7b5a0a4615a4aef6e1a4d2c8e4490c7665
# preserved-source: rescued/part2/ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py
# preserved-source-sha256: 5e88ce4d8959a0e13df6478a7811d6f69bbaa217ecef4728bb1f3bcfd2a28105
"""What: Compare local SVG reference artwork with the current glyph outline.
How: Read the current-master outline and load the whole SVG into a native vector
scene item. Fit and center it, or keep SVG user coordinates in font units.
Draw the glyph in blue above the translucent reference. No SVG bytes are changed.
Why: Compare silhouettes without rasterizing the reference or changing the font.
Usage: Open a glyph. Enter an absolute SVG path and click Compare. Opacity
updates the loaded reference. Compare again after font changes.
Benefit: See proportion differences while designing a glyph in FontLab.
Fit mode normalizes silhouettes. Font units mode keeps SVG user coordinates:
x increases right, y increases downward, and the glyph baseline is y=0.
Neither mode checks imported font metrics.
Animated SVG is refused. Rendering uses the SVG features supported by host Qt.
Setup: FontLab 9, Python 3.11, Fly, fontlabapp and QtSvg.QGraphicsSvgItem.
Independent rewrite of the Qt svgviewer example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
"""

import math
from pathlib import Path
from time import monotonic
from typing import Any

TITLE = "Glyph SVG Reference"
KEY = "drawing_svgviewer"


def capture_outline() -> tuple[str, Any]:
    """Double-check the current context and geometry around a detached Qt path.

    Read only the current-master layer. App resolves transformed components.
    Compare raw geometry, layer and glyph ids, package ids and master before
    returning. Never read the native fgGlyph cache or notify font history.
    """
    import fly.ap.inspectors as inspectors  # noqa: PLR0402 - Fly requires module import
    import fly.ap.node_coordinates as coordinates
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import

    deadline = monotonic() + 2.0

    def context() -> tuple[Any, Any, Any, tuple]:
        if monotonic() >= deadline:
            raise TimeoutError("Outline capture expired; Compare again.")
        package = scripting.current_package()
        if package is None:
            raise ValueError("Open a font and a glyph before Compare.")
        glyph = coordinates.current_glyph(package)
        if glyph is None:
            raise ValueError("Open a glyph before Compare.")
        layer = glyph.findLayer(str(package.master))
        if layer is None or layer.isNull:
            raise ValueError("The glyph has no current-master layer.")
        if int(glyph.package.id) != int(package.id):
            raise ValueError("The current glyph belongs to another font.")
        stamp = (
            int(package.id),
            int(package.fgId),
            str(package.master),
            int(glyph.id),
            int(layer.id),
            str(glyph.name),
        )
        return package, glyph, layer, stamp

    _, _, layer, before = context()
    source = inspectors.outline_source(layer)
    path = inspectors.outline(layer)
    _, _, current_layer, after = context()
    if before != after or source != inspectors.outline_source(current_layer):
        raise ValueError("Font, glyph, master or outline changed; Compare again.")
    if monotonic() >= deadline:
        raise TimeoutError("Outline capture expired; Compare again.")
    if path.isEmpty():
        raise ValueError("The current glyph has no drawable outline.")
    label = f"{before[5]} / {before[2]}"
    if any(
        ord(c) < 32 or c in "\u00a0\u2028\u2029" or 0xD800 <= ord(c) <= 0xDFFF
        for c in label
    ):
        raise ValueError("The glyph or master name cannot be transferred exactly.")
    return label, path


def reference_file(filename: str) -> Path:
    """Read only an explicit existing SVG file; never rewrite its payload."""
    path = Path(filename)
    if not path.is_absolute() or path.suffix.lower() != ".svg" or not path.is_file():
        raise ValueError("Enter an absolute path to an existing .svg file.")
    return path


def alignment_matrix(
    source: tuple[float, ...], target: tuple[float, ...]
) -> tuple[float, ...]:
    """Uniformly fit and center source bounds in target bounds; preserve aspect."""
    if (
        not all(math.isfinite(v) for v in (*source, *target))
        or min(*source[2:], *target[2:]) <= 0
    ):
        raise ValueError("SVG and glyph bounds must have finite positive dimensions.")
    x, y, width, height = source
    tx, ty, tw, th = target
    scale = min(tw / width, th / height)
    result = (
        scale,
        0.0,
        0.0,
        scale,
        tx + (tw - width * scale) / 2 - x * scale,
        ty + (th - height * scale) / 2 - y * scale,
    )
    if not all(math.isfinite(v) for v in result) or scale <= 0:
        raise ValueError("The SVG display scale is outside the finite range.")
    return result


def reference_matrix(
    source: tuple[float, ...],
    viewbox: tuple[float, ...],
    target: tuple[float, ...],
    font_units: bool,
) -> tuple[float, ...]:
    """Restore SVG user coordinates before optional silhouette normalization.

    Qt item bounds use the SVG's default display size. Undo that display mapping
    using the renderer viewBox, including its x/y origin. Keep y downward.
    """
    if (
        not all(math.isfinite(v) for v in (*source, *viewbox))
        or min(*source[2:], *viewbox[2:]) <= 0
    ):
        raise ValueError("SVG bounds and viewBox need finite positive dimensions.")
    x, y, width, height = source
    vx, vy, vw, vh = viewbox
    scale, _, _, _, dx, dy = (
        (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        if font_units
        else alignment_matrix(viewbox, target)
    )
    sx, sy = vw / width, vh / height
    result = (
        sx * scale,
        0.0,
        0.0,
        sy * scale,
        (vx - x * sx) * scale + dx,
        (vy - y * sy) * scale + dy,
    )
    if not all(math.isfinite(v) for v in result):
        raise ValueError("SVG user-coordinate mapping is outside the finite range.")
    return result


def panel_type(qt: Any) -> type:
    """Build an owned vector scene; leave painting and item lifetimes with Qt."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Compare current geometry with a source file in a vector scene."""

        def __init__(self, parent: Any) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.Window)
            self.reference_item = None
            self.reference_boxes = None
            self.view_caption = ""
            self.scope = signals.Scope(self.failure)
            self.terminal = signals.Scope(self.failure)
            self.terminal.connect(
                self.destroyed, lambda *args: self.destroyed_cleanup()
            )
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(780, 600)
            self.stack = gui.QVBoxLayout(self)
            self.stack.setContentsMargins(18, 18, 18, 18)
            intro = gui.QLabel(
                "Blue current glyph over SVG. Choose Fit Silhouette or Font Units (SVG user unit = font unit; baseline y=0).",
                self,
            )
            intro.setWordWrap(True)
            intro.setTextFormat(core.Qt.PlainText)
            self.stack.addWidget(intro)
            self.source_entry = gui.QLineEdit(self)
            self.source_entry.setPlaceholderText("Absolute path to an SVG reference")
            self.stack.addWidget(self.source_entry)
            self.toolbar = gui.QHBoxLayout()
            self.stack.addLayout(self.toolbar)
            self.opacity_control = gui.QDoubleSpinBox(self)
            self.opacity_control.setRange(0.0, 1.0)
            self.opacity_control.setDecimals(2)
            self.opacity_control.setValue(0.35)
            self.toolbar.addWidget(gui.QLabel("Reference opacity", self))
            self.toolbar.addWidget(self.opacity_control)
            self.mode_choice = gui.QComboBox(self)
            self.mode_choice.addItems(["Fit Silhouette", "Font Units"])
            self.toolbar.addWidget(self.mode_choice)
            self.scope.connect(
                self.opacity_control.valueChanged, lambda *args: self.change_opacity()
            )
            self.scope.connect(
                self.mode_choice.currentIndexChanged,
                lambda *args: self.reposition_reference(),
            )
            self.canvas = gui.QGraphicsScene(self)
            self.viewer = gui.QGraphicsView(self.canvas, self)
            self.stack.addWidget(self.viewer)
            self.message = gui.QLabel("Open a glyph and choose a reference.", self)
            self.message.setWordWrap(True)
            self.message.setTextFormat(core.Qt.PlainText)
            self.stack.addWidget(self.message)
            self.add_button("Compare", self.compare)
            self.add_button("Close", lambda: self.close(), closing=True)

        def failure(self, error: Exception) -> None:
            """Show callback errors in the panel, including capture timeouts."""
            self.message.setText(str(error))

        def add_button(self, text: str, action: Any, *, closing: bool = False) -> None:
            """Own each callable and keep failed Close disconnections retryable."""
            control = gui.QPushButton(text, self)
            self.toolbar.addWidget(control)
            self.scope.connect(
                control.clicked, lambda *args: action(), closing=closing, retry=closing
            )

        def compare(self) -> None:
            """Read both inputs fresh; clear any stale or partly built scene on failure."""
            self.clear_scene()
            try:
                svg = getattr(qt, "QtSvg", None)
                if svg is None or not hasattr(svg, "QGraphicsSvgItem"):
                    raise ValueError(
                        "This FontLab Qt build does not expose QGraphicsSvgItem."
                    )
                filename = reference_file(
                    str(properties.value(self.source_entry, "text"))
                )
                label, path = capture_outline()
                flipped = gui.QTransform(1.0, 0.0, 0.0, -1.0, 0.0, 0.0).map(path)
                reference = svg.QGraphicsSvgItem(str(filename))
                # Enroll before validation so every failure clears the item and renderer.
                self.canvas.addItem(reference)
                renderer = reference.renderer()
                if not renderer.isValid():
                    raise ValueError("Qt cannot render this SVG file.")
                if renderer.animated():
                    raise ValueError(
                        "Use a static SVG reference; animated SVG is refused."
                    )
                source = reference.boundingRect()
                target = flipped.boundingRect()

                def box(rectangle: Any) -> tuple[float, ...]:
                    return tuple(
                        float(properties.value(rectangle, name))
                        for name in ("x", "y", "width", "height")
                    )

                renderer.setAspectRatioMode(core.Qt.IgnoreAspectRatio)
                self.reference_boxes = (
                    box(source),
                    box(properties.value(renderer, "viewBoxF")),
                    box(target),
                )
                self.reference_item = reference
                self.view_caption = label
                self.change_opacity()
                if not self.reposition_reference():
                    return
                reference.setZValue(0.0)
                pen = gui.QPen(gui.QColor("#246fb5"))
                pen.setCosmetic(True)
                glyph_item = self.canvas.addPath(
                    flipped, pen, gui.QBrush(core.Qt.NoBrush)
                )
                glyph_item.setZValue(1.0)
                self.reposition_reference()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.clear_scene()
                self.failure(error)

        def clear_scene(self) -> None:
            """Drop item wrappers before scene.clear deletes native objects."""
            self.reference_item = None
            self.reference_boxes = None
            self.canvas.clear()

        def change_opacity(self) -> None:
            """Update only the loaded item; never reread the file or current glyph."""
            try:
                if self.reference_item is not None:
                    self.reference_item.setOpacity(
                        float(properties.value(self.opacity_control, "value"))
                    )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.failure(error)

        def reposition_reference(self) -> bool:
            """Switch placement using cached numeric boxes, without another capture."""
            try:
                if self.reference_item is None or self.reference_boxes is None:
                    return False
                font_units = (
                    int(properties.value(self.mode_choice, "currentIndex")) == 1
                )
                matrix = reference_matrix(*self.reference_boxes, font_units)
                self.reference_item.setTransform(gui.QTransform(*matrix))
                bounds = self.canvas.itemsBoundingRect()
                self.canvas.setSceneRect(bounds)
                self.viewer.fitInView(bounds, core.Qt.KeepAspectRatio)
                mode = (
                    "Font units: SVG user unit = font unit"
                    if font_units
                    else "Fit silhouette: normalized display scale"
                )
                self.message.setText(
                    f"{self.view_caption} — snapshot. {mode}; source file unchanged."
                )
                return True
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.clear_scene()
                self.failure(error)
                return False

        def release(self) -> None:
            """Forget only this panel's registry entry."""
            import sys

            registry = getattr(sys, "_fontlab_samples", {})
            if registry.get(KEY) is self:
                registry.pop(KEY)

        def destroyed_cleanup(self) -> None:
            """Release callbacks after external parent destruction."""
            self.reference_item = None
            self.reference_boxes = None
            self.scope.finish(destroyed=True)
            self.terminal.finish(destroyed=True)
            self.release()

        def closeEvent(self, event: Any) -> None:
            """Disconnect before destroying the scene's native SVG renderer."""
            try:
                if not self.scope.finish() or not self.terminal.finish():
                    event.ignore()
                    return
                self.clear_scene()
                self.release()
                event.accept()
                self.deleteLater()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.failure(error)
                event.ignore()

    return Panel


def main() -> Any:
    """Open via the host registry; never construct another application."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import
    from fly import qt

    try:
        return scripting.show_script_dialog(panel_type(qt), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        qt.QtGui.QMessageBox.warning(None, TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
