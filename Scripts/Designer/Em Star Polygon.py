# this_file: Scripts/Designer/Em Star Polygon.py
# SPDX-License-Identifier: Apache-2.0
# historical source: rescued/part2/ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py
# historical source sha256: c96726078578bad1e6651507493d0a0914a98d35b54ed0553f215c01bdcd3b57
# historical source: rescued/part3/pyqt-official-ports/ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py
# historical source sha256: 4d3016d00e140cfa1985aface43fd8f792dd4fff4b1cb015f9980ea56e0a3481
"""What: Draw a star polygon in the current FontLab layer as one Undo step.
How: Alternate radii in font units, with Y up. Centre the contour on half the
active layer advance and half its associated master's FontMetrics cap height.
Why: Start ornamental glyphs from repeatable, font-sized construction.
Usage: Open a glyph. Set tips, radii in ems and rotation. Generate Preview,
then Draw in Current Layer. Each Draw adds one closed contour in a new shape.
Auto layers and bases of auto composites are refused. Read-back checks the
new contour and verifies every pre-existing shape's geometry. Layers without an
associated master are refused. Draw coordinates use whole-unit half-up rounding
(ties away from zero); read-back allows 0.5 units on each new-node coordinate.
A partial-write error directs you to Edit > Undo.
Benefit: Create geometric artwork directly in the active glyph layer.

The read-only shape preview is centred at the origin; drawing placement uses
the current advance and cap height. Equal radii produce a regular polygon with
twice the tip count. Positive rotation turns counterclockwise.
SVG is secondary output for an external vector editor. Generate Preview, then
copy the SVG text or Save New SVG to a new absolute .svg path. SVG uses a
Y-down em square and contains no font metrics, anchors or hints.
Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless panel.
The App panel owns signals and completion. No painter or plugin is needed.

Independent rewrite of the Qt polygonwidget example idea, David Boddie and
Trolltech ASA. Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
"""

import math
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any


def polygon_points(
    upm: float, tips: int, outer: float, inner: float, rotation: float
) -> list[tuple[float, float]]:
    """Return Y-up points centred at the origin. Radii are em fractions.

    Reject invalid values before computing floating-point coordinates.
    Preview uses these points. SVG formats six decimals; Draw rounds the
    translated points to whole units. Keep both radii inside the em square.
    """
    numbers = (upm, outer, inner, rotation)
    if any(
        isinstance(n, bool)
        or not isinstance(n, (int, float))
        or (isinstance(n, float) and not math.isfinite(n))
        for n in numbers
    ):
        raise ValueError("Use finite numeric UPM, radii and rotation values.")
    if not 16 <= upm <= 16384:
        raise ValueError("Use a font UPM between 16 and 16384.")
    if type(tips) is not int or not 3 <= tips <= 128:
        raise ValueError("Use an integer tip count between 3 and 128.")
    if not 0.001 <= inner <= outer <= 0.5 or not 0 <= rotation <= 360:
        raise ValueError("Use 0.001 <= inner <= outer <= 0.5 em and 0..360 degrees.")
    points: list[tuple[float, float]] = []
    for index in range(tips * 2):
        angle = math.radians(rotation % 360) + index * math.pi / tips
        radius = upm * (outer if index % 2 == 0 else inner)
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    return points


def polygon_svg(
    upm: float, tips: int, outer: float, inner: float, rotation: float
) -> str:
    """Return Y-down SVG in an em square for an external vector editor."""
    points: list[str] = [
        f"{upm / 2 + x:.6f},{upm / 2 - y:.6f}"
        for x, y in polygon_points(upm, tips, outer, inner, rotation)
    ]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {upm:g} {upm:g}" '
        f'width="{upm:g}" height="{upm:g}">\n'
        f'  <polygon fill="black" points="{" ".join(points)}"/>\n</svg>\n'
    )


def current_svg(tips: int, outer: float, inner: float, rotation: float) -> str:
    """Read and fence the current font UPM. Refuse a missing or changed font."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly module import

    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font before generating artwork.")
    identity, upm = package.id, float(package.upm)
    result = polygon_svg(upm, tips, outer, inner, rotation)
    current = scripting.current_package(identity)
    if current is None or float(current.upm) != upm:
        raise ValueError("Font or UPM changed; generate again.")
    return result


def save_svg(filename: str, text: str) -> None:
    """Save generated SVG to a new absolute path; never replace a file or link."""
    path = Path(filename).expanduser()
    if not path.is_absolute() or path.suffix.lower() != ".svg":
        raise ValueError("Enter an absolute destination path ending in .svg.")
    with path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(text)


def round_unit(value: float) -> float:
    """Round a finite coordinate half-up to whole units; ties go away from zero."""
    return float(Decimal(str(value)).to_integral_value(rounding=ROUND_HALF_UP))


def layer_geometry(layer: Any, qt: Any) -> tuple:
    """Snapshot each shape's transform basis, closure and raw/transformed nodes.

    Plain values preserve shape boundaries and order without comparing wrappers
    or shape ids. Both raw and placed points catch compensating transform edits.
    """
    shapes: list[tuple] = []
    for shape in layer.shapes:
        transform = shape.transform
        basis = tuple(
            (float(p.x()), float(p.y()))
            for x, y in ((0, 0), (1, 0), (0, 1))
            for p in [transform.map(qt.QtCore.QPointF(x, y))]
        )
        contours = tuple(
            (
                bool(c.closed),
                tuple(
                    (float(n.x), float(n.y), bool(n.isOn()), float(p.x()), float(p.y()))
                    for n in c.nodes()
                    for p in [transform.map(qt.QtCore.QPointF(n.x, n.y))]
                ),
            )
            for c in shape.contours
        )
        shapes.append((basis, contours))
    return tuple(shapes)


def draw_current(tips: int, outer: float, inner: float, rotation: float) -> None:
    """Append one closed contour, fence context and check attached node geometry."""
    import fly.ap.history as history  # noqa: PLR0402 - Fly module import
    import fly.ap.masters as masters  # noqa: PLR0402 - Fly module import
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly module import
    from fly import fl, qt

    def context() -> tuple[Any, Any, Any, tuple]:
        """Read current ownership, active layer and its actual FontMetrics."""
        package = scripting.current_package()
        if package is None:
            raise ValueError("Open a font before drawing.")
        glyph = fl.CurrentGlyph()
        if glyph is None or glyph.isNull:
            raise ValueError("Open a glyph before drawing.")
        if glyph.package.id != package.id:
            raise ValueError("The active glyph belongs to another font.")
        layer = glyph.activeLayer
        if (
            layer is None
            or layer.isNull
            or layer.id not in {l.id for l in glyph.layers}
        ):
            raise ValueError("The glyph has no owned active layer.")
        width = float(layer.advanceWidth)
        master = masters.associated_master(str(layer.name), tuple(package.masters))
        if master is None:
            raise ValueError(
                "The active layer has no associated master; choose a master layer or its named backup."
            )
        cap = float(fl.FontMetrics(package, master).capsHeight)
        if not math.isfinite(width):
            raise ValueError("The current layer advance must be finite.")
        if not math.isfinite(cap) or cap <= 0:
            raise ValueError(
                "The current layer cap height must be finite and positive."
            )
        return (
            package,
            glyph,
            layer,
            (
                package.id,
                glyph.id,
                layer.id,
                str(layer.name),
                width,
                cap,
                float(package.upm),
                str(package.master),
                master,
            ),
        )

    package, glyph, layer, before = context()
    points = [
        (round_unit(x + before[4] / 2), round_unit(y + before[5] / 2))
        for x, y in polygon_points(before[6], tips, outer, inner, rotation)
    ]
    facts = history.scan_auto_facts(package)
    if context()[3] != before:
        raise ValueError("Font, glyph, layer or metrics changed; draw again.")
    original = layer_geometry(layer, qt)
    original_count = len(original)
    nodes = [fl.flNode(qt.QtCore.QPointF(x, y), nodeType="on") for x, y in points]
    contour = fl.flContour(nodes, closed=True)
    shape = fl.flShape()
    shape.addContour(contour)

    def mutate() -> None:
        """Recheck the bound inputs immediately before attaching the new shape."""
        if context()[3] != before or layer_geometry(layer, qt) != original:
            raise ValueError("Font, glyph, layer or geometry changed; draw again.")
        layer.addShape(shape)

    def read_back() -> list[str]:
        """Read the attached copy, including closure, node types and coordinates."""
        actual_shapes = layer_geometry(layer, qt)
        if context()[3] != before or len(actual_shapes) != original_count + 1:
            return ["Current context or shape count differs from the plan."]
        if actual_shapes[:-1] != original:
            return ["Pre-existing shape geometry changed."]
        contours = actual_shapes[-1][1]
        if len(contours) != 1 or not contours[0][0]:
            return ["The attached shape must hold one closed contour."]
        actual = contours[0][1]
        if len(actual) != len(points) or any(
            not n[2]
            or not math.isclose(n[3], x, abs_tol=0.5, rel_tol=0)
            or not math.isclose(n[4], y, abs_tol=0.5, rel_tol=0)
            for n, (x, y) in zip(actual, points, strict=False)
        ):
            return ["Attached polygon node coordinates or types differ from the plan."]
        return []

    result = history.commit(
        "Draw Em Star Polygon",
        [layer],
        [glyph],
        mutate,
        operation="geometry",
        facts=facts,
        read_back=read_back,
    )
    if result.mismatches:
        raise RuntimeError(" ".join(result.mismatches) + " " + history.UNDO_HINT)


def main() -> Any:
    """Open the shared App panel. Keep native imports lazy until menu use."""
    import fly.ap.qt_properties as properties
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly module import
    from fly import qt

    gui = qt.QtGui
    base = scripting.names_dialog_type()

    class Panel(base):
        """Collect shape parameters and save artwork from fresh current UPM."""

        def __init__(self, parent: Any) -> None:
            """Build labelled controls and exact, selectable SVG output."""
            base.__init__(self, parent, "Em Star Polygon", "designer_em_star")
            self.subtitle.setText(
                "Preview the shape, then draw in the active layer. SVG is for an external vector editor."
            )
            self.tips = gui.QSpinBox()
            self.tips.setRange(3, 128)
            self.tips.setValue(5)
            self.root.addWidget(gui.QLabel("Outer tips (3–128)"))
            self.root.addWidget(self.tips)
            self.outer, self.inner, self.rotation = (
                gui.QDoubleSpinBox(),
                gui.QDoubleSpinBox(),
                gui.QDoubleSpinBox(),
            )
            for label, control, low, high, default in (
                ("Outer radius (em)", self.outer, 0.001, 0.5, 0.45),
                ("Inner radius (em)", self.inner, 0.001, 0.5, 0.2),
                ("Rotation (degrees, counterclockwise)", self.rotation, 0, 360, 90),
            ):
                control.setRange(low, high)
                control.setDecimals(3)
                control.setValue(default)
                self.root.addWidget(gui.QLabel(label))
                self.root.addWidget(control)
            self.output = gui.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.destination = gui.QLineEdit()
            self.destination.setPlaceholderText("Absolute path to a NEW .svg file")
            self.status = gui.QLabel("Generate SVG using the current font UPM.")
            self.status.setTextFormat(qt.QtCore.Qt.PlainText)
            self.status.setWordWrap(True)
            self.preview_scene = gui.QGraphicsScene(self)
            self.preview_view = gui.QGraphicsView(self.preview_scene, self)
            self.preview_view.setInteractive(False)
            self.preview_view.setMinimumHeight(180)
            self.preview_view.setBackgroundBrush(
                gui.QBrush(qt.QtCore.Qt.GlobalColor(qt.QtCore.Qt.white))
            )
            self.generate_button = gui.QPushButton("Generate Preview and SVG")
            self.draw_button = gui.QPushButton("Draw in Current Layer")
            self.save_button = gui.QPushButton("Save New SVG")
            self.close_button = gui.QPushButton("Close")
            for control in (
                self.generate_button,
                self.preview_view,
                self.draw_button,
                self.output,
                self.destination,
                self.save_button,
                self.status,
                self.close_button,
            ):
                self.root.addWidget(control)
            self._connect(
                self.generate_button.clicked, lambda *args: self.publish(False)
            )
            self._connect(self.save_button.clicked, lambda *args: self.publish(True))
            self._connect(self.draw_button.clicked, lambda *args: self.draw_polygon())
            self._connect(self.close_button.clicked, lambda *args: self.close())
            self.resize(660, 700)

        def parameters(self) -> tuple[int, float, float, float]:
            """Read property values once for one preview, save or draw action."""
            return (
                int(properties.value(self.tips, "value")),
                float(properties.value(self.outer, "value")),
                float(properties.value(self.inner, "value")),
                float(properties.value(self.rotation, "value")),
            )

        def draw_polygon(self) -> None:
            """Add one contour or show the shared refusal/recovery message."""
            try:
                draw_current(*self.parameters())
                self.status.setText(
                    "Drawn one closed contour. Edit > Undo removes this action."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def publish(self, save: bool) -> None:
            """Preview fresh artwork; retain exact output when only saving fails."""
            self.output.setPlainText("")
            self.preview_scene.clear()
            try:
                parameters = self.parameters()
                text = current_svg(*parameters)
                self.output.setPlainText(text)
                if str(self.output.toPlainText()) != text:
                    raise ValueError("Qt changed the SVG text; export refused.")
                # Unit-em preview shares the same proportions and Y-up orientation.
                points = polygon_points(1000, *parameters)
                polygon = gui.QPolygonF([qt.QtCore.QPointF(x, -y) for x, y in points])
                self.preview_scene.addPolygon(
                    polygon,
                    gui.QPen(qt.QtCore.Qt.PenStyle(qt.QtCore.Qt.NoPen)),
                    gui.QBrush(qt.QtCore.Qt.GlobalColor(qt.QtCore.Qt.black)),
                )
                self.preview_scene.setSceneRect(-550, -550, 1100, 1100)
                self.preview_view.fitInView(
                    -550, -550, 1100, 1100, qt.QtCore.Qt.KeepAspectRatio
                )
                self.status.setText(
                    "Preview ready. Draw in Current Layer, or save SVG for an external vector editor."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output.setPlainText("")
                self.preview_scene.clear()
                self.status.setText(str(error))
                return
            if save:
                try:
                    save_svg(str(properties.value(self.destination, "text")), text)
                    self.status.setText("Saved new SVG for an external vector editor.")
                except (ValueError, RuntimeError, OSError) as error:
                    self.status.setText(str(error))

    return scripting.show_script_dialog(Panel, "designer_em_star")


if __name__ == "__main__":
    main()
