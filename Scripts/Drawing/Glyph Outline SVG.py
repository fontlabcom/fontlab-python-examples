# this_file: Scripts/Drawing/Glyph Outline SVG.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source: rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py
# preserved-source-sha256: ae79ea27f4bb5bb28912a0d9c5ceb8524f3f1c09ca7161bd408bc0e6ca88efb3
# preserved-source: rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/transformations-c12a2071adbab88b.py
# preserved-source-sha256: 533857ee814a9428e094f1ad7dc9c13b4dbe8476c991effaced2f8486bec5abc
# preserved-source: rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/basicdrawing-907f39d8bf387501.py
# preserved-source-sha256: 94c7a27d22a78955265a73c0d98383088c334d50d100eb330b242b84fbee0bab
# preserved-source: rescued/part2/ports/painting/pyqt-official/basicdrawing-907f39d8bf387501.py
# preserved-source-sha256: ee842206b60ab167e4f45919a779a784e7154c2d201f1fad86b389d6436575b8
# preserved-source: rescued/part2/ports/painting/pyqt-official/transformations-c12a2071adbab88b.py
# preserved-source-sha256: af4e3e14274a354fcc26514a063d8d9ba38d6f5930cf272fc4cb28543be1ebcc
# preserved-source: rescued/part2/ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py
# preserved-source-sha256: daa00fe5bed6797d682cb3b219d56fc73d8a0ec8b094144281efa69939008db7
"""What: Export the current glyph outline as reusable SVG artwork.
How: Capture its current-master Qt path, including transformed components.
Choose winding or odd-even fill to diagnose counters and overlaps.
Why: Keep curves in a vector proof without changing font data.
Usage: Open a glyph, Capture, choose a fill rule and Update Proof.
Copy SVG or enter a new absolute .svg path and Save SVG.
Benefit: Keep rendered artwork for an external vector editor.
The frame includes the origin, advance, ascender, descender and ink bounds.
One SVG user unit equals one font unit. SVG y increases downward; baseline is y=0.

SVG is a visual proof. It contains no anchors, metrics, hints or raw node flags.
Snapshots remain detached. Capture again after changing the current font.
Setup: FontLab 9, Python 3.11, Fly, fontlabapp and QtSvg.QSvgGenerator.
Independent rewrite of the Qt painterpaths, basicdrawing and transformations
example ideas (Qt/Nokia, Riverbank). Consolidated into one outline exporter.
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
"""

TITLE = "Glyph Outline SVG"
KEY = "drawing_painterpaths"
HELP = "Capture the current outline. Compare winding and odd-even fills, then save reusable SVG artwork."

import math
import re
from pathlib import Path
from time import monotonic
from typing import Any


def capture_outline() -> tuple[str, Any, tuple[float, float, float]]:
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
            raise TimeoutError("Outline capture expired; capture again.")
        package = scripting.current_package()
        if package is None:
            raise ValueError("Open a font and a glyph before Capture.")
        glyph = coordinates.current_glyph(package)
        if glyph is None:
            raise ValueError("Open a glyph before Capture.")
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
            (
                float(layer.advanceWidth),
                float(package.descender_value),
                float(package.ascender_value),
            ),
        )
        return package, glyph, layer, stamp

    _, _, layer, before = context()
    source = inspectors.outline_source(layer)
    path = inspectors.outline(layer)
    _, _, current_layer, after = context()
    if before != after or source != inspectors.outline_source(current_layer):
        raise ValueError("Font, glyph, master or outline changed; Capture again.")
    if monotonic() >= deadline:
        raise TimeoutError("Outline capture expired; capture again.")
    if path.isEmpty():
        raise ValueError("The current glyph has no drawable outline.")
    label = f"{before[5]} / {before[2]}"
    if any(
        ord(c) < 32 or c in "\u00a0\u2028\u2029" or 0xD800 <= ord(c) <= 0xDFFF
        for c in label
    ):
        raise ValueError("The glyph or master name cannot be transferred exactly.")
    return label, path, before[6]


def font_frame(
    path: Any, metrics: tuple[float, float, float]
) -> tuple[int, int, int, int]:
    """Unite ink with origin and metrics; round outward to whole font units.

    Equal integer viewport and viewBox dimensions keep user units at 1:1.
    Outward rounding retains fractional overhangs without translating artwork.
    """
    import fly.ap.qt_properties as properties

    advance, descender, ascender = metrics
    rect = path.boundingRect()
    x, y, width, height = (
        float(properties.value(rect, name)) for name in ("x", "y", "width", "height")
    )
    if (
        not all(math.isfinite(v) for v in (*metrics, x, y, width, height))
        or descender >= ascender
        or min(width, height) < 0
    ):
        raise ValueError(
            "Use finite outline bounds and ordered font ascender/descender metrics."
        )
    left, bottom = math.floor(min(0, advance, x)), math.floor(min(0, descender, y))
    right, top = (
        math.ceil(max(0, advance, x + width)),
        math.ceil(max(0, ascender, y + height)),
    )
    if not 0 < right - left <= 2147483647 or not 0 < top - bottom <= 2147483647:
        raise ValueError("The font-unit frame is outside Qt's document size range.")
    return left, bottom, right - left, top - bottom


def suggested_svg_path(label: str) -> str:
    """Suggest an absolute Desktop filename; never create a directory or file."""
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", label).strip("._") or "glyph"
    return str(Path.home() / "Desktop" / f"{name}.svg")


def svg_text(qt: Any, path: Any, label: str, frame: tuple[int, int, int, int]) -> str:
    """Let Qt serialize the complete painted path; preserve curves and fill rule.

    SVG is visual artwork, not a source-font backup: anchors, metrics, hints,
    names and raw node flags are not exported. Invert y once for SVG coordinates.
    Always end the owned painter, including errors, before releasing its buffer.
    """
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore
    svg = getattr(qt, "QtSvg", None)
    if svg is None or not hasattr(svg, "QSvgGenerator"):
        raise ValueError("This FontLab Qt build does not expose QSvgGenerator.")
    flipped = gui.QTransform(1.0, 0.0, 0.0, -1.0, 0.0, 0.0).map(path)
    x, bottom, width, height = frame
    bounds = core.QRectF(float(x), float(-bottom - height), float(width), float(height))
    buffer = core.QBuffer()
    if not buffer.open(core.QIODevice.OpenMode(core.QIODevice.WriteOnly)):
        raise RuntimeError("Cannot open the SVG output buffer.")
    try:
        generator = svg.QSvgGenerator()
        generator.setOutputDevice(buffer)
        generator.setSize(core.QSize(width, height))
        generator.setViewBox(bounds)
        generator.setTitle(label)
        generator.setDescription("Rendered FontLab glyph artwork; no font metadata.")
        painter = gui.QPainter()
        try:
            if not painter.begin(generator):
                raise RuntimeError("Cannot start the SVG painter.")
            painter.setPen(gui.QPen(core.Qt.NoPen))
            painter.setBrush(gui.QBrush(gui.QColor("#182a35")))
            painter.drawPath(flipped)
        except Exception as error:
            raise RuntimeError(f"SVG drawing failed: {error}") from error
        finally:
            painter.end()
        payload = properties.value(buffer, "data").data()
        text = payload.decode("utf-8") if isinstance(payload, bytes) else str(payload)
        if "<svg" not in text or "</svg>" not in text:
            raise RuntimeError("Qt returned incomplete SVG output.")
        return text
    finally:
        buffer.close()


def save_svg(filename: str, text: str) -> None:
    """Save an explicit absolute SVG path once; refuse overwrites and empty output."""
    target = Path(filename)
    if not target.is_absolute() or target.suffix.lower() != ".svg" or not text:
        raise ValueError("Enter an absolute .svg path and Capture a result first.")
    try:
        with target.open("x", encoding="utf-8", newline="") as stream:
            stream.write(text)
    except FileExistsError as error:
        raise ValueError(
            "The output file already exists; choose a new path."
        ) from error
    except OSError as error:
        raise ValueError(
            f"Cannot save SVG; a partial file may remain: {error}"
        ) from error


def panel_type(qt: Any) -> type:
    """Bind a modeless snapshot panel to FontLab's Qt and owned signal scope."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own a detached outline snapshot and its exported artwork."""

        def __init__(self, parent: Any) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.Window)
            self.result = ""
            self.snapshot = None
            self.metrics = (0.0, 0.0, 0.0)
            self.suggested_name = ""
            self.caption = ""
            self.scope = signals.Scope(self.failure)
            self.terminal = signals.Scope(self.failure)
            self.terminal.connect(
                self.destroyed, lambda *args: self.destroyed_cleanup()
            )
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(820, 640)
            self.stack = gui.QVBoxLayout(self)
            self.stack.setContentsMargins(18, 18, 18, 18)
            self.intro = gui.QLabel(HELP, self)
            self.intro.setWordWrap(True)
            self.intro.setTextFormat(core.Qt.PlainText)
            self.stack.addWidget(self.intro)
            self.controls = gui.QHBoxLayout()
            self.stack.addLayout(self.controls)
            self.build_controls()
            self.canvas = gui.QGraphicsScene(self)
            self.viewer = gui.QGraphicsView(self.canvas, self)
            self.stack.addWidget(self.viewer)
            self.output_box = gui.QPlainTextEdit(self)
            self.output_box.setReadOnly(True)
            self.output_box.setMaximumHeight(120)
            self.stack.addWidget(self.output_box)
            self.file_entry = gui.QLineEdit(self)
            self.file_entry.setPlaceholderText("Absolute path for a new .svg file")
            self.stack.addWidget(self.file_entry)
            self.action_row = gui.QHBoxLayout()
            self.stack.addLayout(self.action_row)
            self.message = gui.QLabel(
                "Capture reads the current glyph. No font edits.", self
            )
            self.message.setTextFormat(core.Qt.PlainText)
            self.message.setWordWrap(True)
            self.stack.addWidget(self.message)
            self.add_button("Capture", self.capture_result)
            self.add_button("Update Proof", self.refresh_proof)
            self.add_button("Copy SVG", self.copy_svg)
            self.add_button("Save SVG", self.save_result)
            self.add_button("Close", lambda: self.close(), closing=True)

        def failure(self, error: Exception) -> None:
            """Report slot errors without allowing exceptions into PythonQt."""
            self.message.setText(str(error))

        def add_button(self, label: str, action: Any, *, closing: bool = False) -> None:
            """Own the exact callable pair; Close remains available for retry."""
            control = gui.QPushButton(label, self)
            self.action_row.addWidget(control)
            self.scope.connect(
                control.clicked, lambda *args: action(), closing=closing, retry=closing
            )

        def clear_output(self) -> None:
            """Disable stale export before a capture or proof calculation."""
            self.result = ""
            self.canvas.clear()
            self.output_box.setPlainText("")

        def capture_result(self) -> None:
            """Read an entire snapshot or discard it after any failed refresh."""
            self.snapshot = None
            self.clear_output()
            try:
                self.caption, self.snapshot, self.metrics = capture_outline()
                current_name = str(properties.value(self.file_entry, "text"))
                if not current_name or current_name == self.suggested_name:
                    self.suggested_name = suggested_svg_path(self.caption)
                    self.file_entry.setText(self.suggested_name)
                self.refresh_proof()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.failure(error)

        def refresh_proof(self) -> None:
            """Draw detached geometry and prepare durable SVG artwork."""
            self.clear_output()
            try:
                if self.snapshot is None:
                    raise ValueError("Capture a glyph before Update Proof.")
                path = self.proof_path()
                frame = font_frame(path, self.metrics)
                text = svg_text(qt, path, self.caption, frame)
                self.output_box.setPlainText(text)
                if str(self.output_box.toPlainText()) != text:
                    raise ValueError("Qt changed the SVG text; export is disabled.")
                flipped = gui.QTransform(1.0, 0.0, 0.0, -1.0, 0.0, 0.0).map(path)
                self.canvas.addPath(
                    flipped, gui.QPen(core.Qt.NoPen), gui.QBrush(gui.QColor("#182a35"))
                )
                x, bottom, width, height = frame
                bounds = core.QRectF(
                    float(x), float(-bottom - height), float(width), float(height)
                )
                self.canvas.setSceneRect(bounds)
                self.viewer.fitInView(bounds, core.Qt.KeepAspectRatio)
                self.result = text
                self.message.setText(
                    self.caption
                    + " — snapshot. Save SVG for an external vector editor; Capture after font changes."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.clear_output()
                self.failure(error)

        def copy_svg(self) -> None:
            """Export the displayed snapshot; edits to controls require Update Proof."""
            try:
                if not self.result:
                    raise ValueError("Capture or Update Proof before copying.")
                gui.QApplication.clipboard().setText(self.result)
                self.message.setText("SVG copied for an external vector editor.")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.failure(error)

        def save_result(self) -> None:
            """Save artwork for an external vector editor."""
            try:
                save_svg(str(properties.value(self.file_entry, "text")), self.result)
                self.message.setText(
                    "SVG saved for an external vector editor; font metadata is not included."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.failure(error)

        def release(self) -> None:
            """Forget only this panel's registry entry."""
            import sys

            registry = getattr(sys, "_fontlab_samples", {})
            if registry.get(KEY) is self:
                registry.pop(KEY)

        def destroyed_cleanup(self) -> None:
            """Fence callbacks and release Python references after parent destruction."""
            self.scope.finish(destroyed=True)
            self.terminal.finish(destroyed=True)
            self.snapshot = None
            self.release()

        def closeEvent(self, event: Any) -> None:
            """Drain callbacks before deletion; retain the panel on disconnect failure."""
            try:
                if not self.scope.finish() or not self.terminal.finish():
                    event.ignore()
                    return
                self.snapshot = None
                self.release()
                event.accept()
                self.deleteLater()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.failure(error)
                event.ignore()

        def build_controls(self) -> None:
            """Offer the two Qt fill rules for counter and overlap diagnosis."""
            self.fill_choice = gui.QComboBox(self)
            self.fill_choice.addItems(["Winding fill", "Odd-even fill"])
            self.controls.addWidget(self.fill_choice)

        def proof_path(self) -> Any:
            """Copy the detached path before changing its visual fill rule."""
            path = gui.QPainterPath(self.snapshot)
            rule = (
                core.Qt.OddEvenFill
                if int(properties.value(self.fill_choice, "currentIndex"))
                else core.Qt.WindingFill
            )
            path.setFillRule(rule)
            return path

    return Panel


def main() -> Any:
    """Use FontLab's existing application and App's retained panel registry."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module import
    from fly import qt

    try:
        return scripting.show_script_dialog(panel_type(qt), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        qt.QtGui.QMessageBox.warning(None, TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
