# this_file: Scripts/Widgets/Glyph Sketch Pad.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/scribble-8e5aa13798c2763c.py
# preserved-source-sha256: 758bb2e898a2975343743f36ae11481cf14a3cee0094558998dcd70ccb1df640
# preserved-source: rescued/part2/ports/widgets/pyqt-official/scribble-8e5aa13798c2763c.py
# preserved-source-sha256: 190d94c10462c2d149efb79fa2f885bf62f55c44bb60addf45bf862f04f2c9a5
"""What: Sketch construction ideas over a detached current-glyph outline.
How: Capture the current glyph in the current master. Fit its complete Qt path
into an owned canvas. Use its Base and Text palette roles for painting. Store
pen strokes in font units with y increasing upward. SVG keeps a fixed stroke.
Why: A detached sketch protects the glyph while keeping meaningful coordinates.
Usage: Open a glyph, then Capture. Drag to draw. Undo Stroke removes one stroke;
Clear removes the local sketch. SVG Text produces strokes for an external vector
editor, without the reference outline. Copy SVG Text before closing to retain it.
Capture refuses to replace a nonempty sketch. Close drops scratch strokes and
always permits application quit. No font or filesystem writes occur.
Benefit: Explore construction changes beside FontLab and keep reusable SVG lines.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless panel. App owns
signals and completion.
Independent rewrite of the Qt Scribble example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.
"""

import math
from html import escape
from itertools import pairwise
from time import monotonic
from typing import Any

Point = tuple[float, float]
Box = tuple[float, float, float, float]
MAX_POINTS = 20000


def sketch_svg(label: str, strokes: list[list[Point]], box: Box) -> str:
    """Return only pen strokes as SVG. Keep coordinates in font units."""
    if not strokes or not any(strokes):
        raise ValueError("Draw a stroke before preparing SVG text.")
    x, y, width, height = box
    values = (*box, *(v for stroke in strokes for point in stroke for v in point))
    if not all(math.isfinite(v) for v in values) or width <= 0 or height <= 0:
        raise ValueError("Sketch coordinates and a positive view box must be finite.")
    if sum(map(len, strokes)) > MAX_POINTS:
        raise ValueError("Sketch point limit exceeded; clear or undo a stroke.")
    if any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF for c in label):
        raise ValueError("The glyph label cannot be represented as XML text.")
    paths = "".join(
        '<polyline points="' + " ".join(f"{px:g},{py:g}" for px, py in stroke) + '"/>'
        for stroke in strokes
        if stroke
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:g} {0 - y - height:g} {width:g} {height:g}">'
        + f"<title>Sketch for {escape(label)}</title>"
        + '<g transform="scale(1,-1)" fill="none" stroke="#246fb5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        + paths
        + "</g></svg>"
    )


def capture_outline() -> tuple[str, Any, Box]:
    """Capture once under a deadline. Never read the mutating fgGlyph getter."""
    import fly.ap.inspectors as inspectors  # noqa: PLR0402 - Fly requires module imports
    import fly.ap.node_coordinates as coordinates
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module imports

    deadline = monotonic() + 2
    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font and a glyph before capturing an outline.")
    identity, master, upm = package.id, str(package.master), float(package.upm)
    glyph = coordinates.current_glyph(package)
    if glyph is None:
        raise ValueError("Open a glyph before capturing an outline.")
    name = str(glyph.name)
    layer = glyph.findLayer(master)
    if layer is None or layer.isNull:
        raise ValueError("The current glyph has no layer in the current master.")
    path = inspectors.outline(layer)
    current = scripting.current_package(identity)
    current_glyph = coordinates.current_glyph(current) if current is not None else None
    if (
        current is None
        or str(current.master) != master
        or float(current.upm) != upm
        or current_glyph is None
        or str(current_glyph.name) != name
    ):
        raise ValueError("Glyph, font or master changed; capture again.")
    if monotonic() >= deadline:
        raise TimeoutError("Outline capture expired; no partial result.")
    if not math.isfinite(upm) or upm <= 0:
        raise ValueError("The current font has an invalid UPM.")
    bounds = path.boundingRect()
    x, y = min(0.0, float(bounds.x())), min(0.0, float(bounds.y()))
    right, top = max(upm, float(bounds.right())), max(upm, float(bounds.bottom()))
    pad = upm * 0.1
    box = (x - pad, y - pad, right - x + 2 * pad, top - y + 2 * pad)
    if not all(math.isfinite(v) for v in box):
        raise ValueError("Outline bounds are not finite.")
    return f"{name} / {master}", path, box


def canvas_type(qt: Any, status: Any, changed: Any) -> type:
    """Create a bounded local canvas. Contain every native event boundary."""
    import fly.ap.qt_properties as properties

    g, core = qt.QtGui, qt.QtCore

    class Canvas(g.QWidget):
        """Own only detached paths and Python stroke coordinates."""

        def __init__(self, parent: Any) -> None:
            g.QWidget.__init__(self, parent)
            self.reference_path: Any = None
            self.view_box: Box = (0, 0, 1000, 1000)
            self.strokes: list[list[Point]] = []
            self.drawing = False
            self.point_count = 0
            self.setMinimumSize(360, 360)

        def mapping(self) -> tuple[float, float, float]:
            """Fit the font box with centered margins, preserving aspect ratio."""
            width, height = (
                float(properties.value(self, "width")),
                float(properties.value(self, "height")),
            )
            _, _, bw, bh = self.view_box
            scale = min(max(width, 1) / bw, max(height, 1) / bh)
            return scale, (width - bw * scale) / 2, (height - bh * scale) / 2

        def point(self, event: Any) -> Point:
            """Convert widget pixels to font units; never negate a Qt wrapper."""
            scale, left, top = self.mapping()
            x, y, _, height = self.view_box
            return x + (event.x() - left) / scale, y + height - (
                event.y() - top
            ) / scale

        def paintEvent(self, event: Any) -> None:
            """End the painter in finally even when a detached path fails to draw."""
            painter: Any = None
            try:
                painter = g.QPainter(self)
                painter.setRenderHint(g.QPainter.Antialiasing, True)
                palette = properties.value(self, "palette")
                group = palette.currentColorGroup()
                background = palette.color(group, g.QPalette.Base)
                foreground = palette.color(group, g.QPalette.Text)
                reference = g.QColor(foreground)
                reference.setAlpha(64)
                painter.fillRect(properties.value(self, "rect"), background)
                scale, left, top = self.mapping()
                x, y, _, height = self.view_box
                painter.translate(left, top)
                painter.scale(scale, 0 - scale)
                painter.translate(0 - x, 0 - y - height)
                if self.reference_path is not None:
                    painter.fillPath(self.reference_path, g.QBrush(reference))
                painter.setPen(g.QPen(g.QBrush(foreground), 2.0 / scale))
                for stroke in self.strokes:
                    for first, second in pairwise(stroke):
                        painter.drawLine(core.QPointF(*first), core.QPointF(*second))
            except Exception as error:  # noqa: BLE001 - exceptions must not leave native paintEvent
                status.setText(f"Sketch paint failed: {error}")
            finally:
                if painter is not None:
                    try:
                        painter.end()
                    except Exception as error:  # noqa: BLE001 - contain painter teardown
                        status.setText(f"Sketch painter cleanup failed: {error}")

        def mousePressEvent(self, event: Any) -> None:
            """Start a new local stroke only after a successful outline capture."""
            try:
                if event.button() != core.Qt.LeftButton or self.reference_path is None:
                    return
                if self.point_count >= MAX_POINTS:
                    raise ValueError(
                        "Sketch point limit reached; Clear or Undo Stroke."
                    )
                self.strokes.append([self.point(event)])
                self.point_count += 1
                self.drawing = True
                changed()
            except Exception as error:  # noqa: BLE001 - native event boundary
                self.drawing = False
                status.setText(str(error))

        def mouseMoveEvent(self, event: Any) -> None:
            """Append bounded points. Stop before event-loop work grows unbounded."""
            try:
                if not self.drawing:
                    return
                if self.point_count >= MAX_POINTS:
                    raise ValueError(
                        "Sketch point limit reached; Clear or Undo Stroke."
                    )
                point = self.point(event)
                if point != self.strokes[-1][-1]:
                    self.strokes[-1].append(point)
                    self.point_count += 1
                    changed()
                    self.update()
            except Exception as error:  # noqa: BLE001 - native event boundary
                self.drawing = False
                status.setText(str(error))

        def mouseReleaseEvent(self, event: Any) -> None:
            """Finish a stroke. Preserve a click as a short visible mark."""
            try:
                if self.drawing:
                    self.mouseMoveEvent(event)
                    stroke = self.strokes[-1]
                    if len(stroke) == 1 and self.point_count < MAX_POINTS:
                        x, y = stroke[0]
                        stroke.append((x + 0.1, y))
                        self.point_count += 1
                    self.update()
            except Exception as error:  # noqa: BLE001 - native event boundary
                status.setText(str(error))
            finally:
                self.drawing = False

    return Canvas


def main() -> Any:
    """Open the modeless App shell with a detached vector sketch surface."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module imports
    from fly import qt

    g, base = qt.QtGui, scripting.names_dialog_type()

    class Dialog(base):
        """Keep scratch strokes local and expose copyable SVG text."""

        def __init__(self, parent: Any) -> None:
            base.__init__(self, parent, "Glyph Sketch Pad", "widgets_glyph_sketch_pad")
            self.subtitle.setText(
                "Capture current glyph/current master. Draw locally. SVG Text exports strokes only."
            )
            self.status = g.QLabel("Capture an open glyph to start.")
            self.status.setTextFormat(qt.QtCore.Qt.PlainText)
            self.status.setWordWrap(True)
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.glyph_label = ""
            self.canvas = canvas_type(qt, self.status, self.edited)(self)
            self.root.addWidget(self.canvas)
            self.root.addWidget(self.output)
            for text, action in (
                ("Capture", self.preview),
                ("Undo Stroke", self.undo_stroke),
                ("Clear", self.clear_sketch),
                ("SVG Text", self.svg_text),
                ("Close", self.close),
            ):
                button = g.QPushButton(text)
                self.root.addWidget(button)
                self._connect(
                    button.clicked, lambda *args, action=action: self.run(action)
                )
            self.root.addWidget(self.status)
            self.resize(640, 720)

        def run(self, action: Any) -> None:
            """Contain failed native reads and local SVG validation errors."""
            try:
                action()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def edited(self) -> None:
            """Invalidate prepared SVG immediately after any pen change."""
            self.output.setPlainText("")
            self.status.setText(
                "Scratch sketch. Copy SVG Text before closing to retain it."
            )

        def preview(self) -> None:
            """Replace only an empty sketch. Clear a failed reference capture."""
            if self.canvas.strokes:
                self.status.setText(
                    "Clear or Undo Stroke before capturing another glyph."
                )
                return
            self.canvas.reference_path = None
            self.glyph_label = ""
            self.output.setPlainText("")
            try:
                label, path, box = capture_outline()
                self.glyph_label, self.canvas.reference_path, self.canvas.view_box = (
                    label,
                    path,
                    box,
                )
                self.status.setText(
                    "Captured " + label + ". Draw over this detached outline."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))
            self.canvas.update()

        def undo_stroke(self) -> None:
            """Remove only the latest local stroke; FontLab history is untouched."""
            self.canvas.drawing = False
            if self.canvas.strokes:
                self.canvas.point_count -= len(self.canvas.strokes.pop())
            self.edited()
            self.canvas.update()

        def clear_sketch(self) -> None:
            """Explicitly discard all pen strokes while retaining the reference."""
            self.canvas.drawing = False
            self.canvas.strokes.clear()
            self.canvas.point_count = 0
            self.edited()
            self.canvas.update()

        def svg_text(self) -> None:
            """Publish a selectable stroke-only SVG for an external vector editor."""
            self.output.setPlainText("")
            text = sketch_svg(
                self.glyph_label, self.canvas.strokes, self.canvas.view_box
            )
            self.output.setPlainText(text)
            if str(self.output.toPlainText()) != text:
                self.output.setPlainText("")
                raise ValueError("Qt changed SVG text; copy refused.")
            self.status.setText(
                "Select and copy SVG text. The grey reference outline is not included."
            )

        def closeEvent(self, event: Any) -> None:
            """Allow ordinary close and application quit; release scratch strokes."""
            self.canvas.drawing = False
            base.closeEvent(self, event)

    return scripting.show_script_dialog(Dialog, "widgets_glyph_sketch_pad")


if __name__ == "__main__":
    main()
