# this_file: Scripts/Tools/Path Problem Report.py
# SPDX-License-Identifier: Apache-2.0
"""What: Report contour problems on the current font's current master.
How: Inspect each glyph's contours once. List open contours, closed contours with fewer
than three on-curve nodes, equal adjacent nodes and small node extents.
Why: A combined report gives one repair checklist before overlap removal.
Usage: Open a font. Set the minimum extent, then Refresh. Enter an absolute
new JSON filename and Export to save the complete captured checklist.
Benefit: A build check or another FontLab script can consume the JSON file.

Small extents use node coordinates, including control points, in shape space.
They are a diagnostic heuristic, not exact curve bounds. The report does not
flatten components. Missing master layers are listed separately. No font data
changes. Use Select glyphs with findings after activating the Font window.
Scriptmix Reports > Open Contours is the master-wide variant that selects glyphs.
This tool adds a combined checklist and complete JSON export for build checks.
Scanning runs in small UI-thread steps; Cancel discards the entire unfinished
report. Font, master, glyph order and modification-date changes reject the scan.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Based on the author's own FontLab sample, Apache-2.0.
Sources: recipe.py and path_report.py (Path Problem Report).
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterable
from pathlib import Path
from threading import current_thread, main_thread
from time import monotonic
from typing import Any

TITLE = "Path Problem Report"
_PANELS: list[Any] = []
GLYPHS_PER_TICK = 32
STEP_SECONDS = 0.03


def diagnose(contours: Iterable[Any], threshold: float) -> list[dict[str, Any]]:
    """Return one record per finding; closed seams are adjacent too.

    Empty closed contours have zero on-curve nodes. Open contours keep their
    endpoints distinct. An extent exactly at the threshold is not small.
    """
    if not math.isfinite(threshold) or threshold < 0:
        raise ValueError("Minimum extent must be finite and nonnegative.")
    findings: list[dict[str, Any]] = []
    for index, contour in enumerate(contours, 1):
        nodes = list(contour.nodes())
        points = [(float(node.x), float(node.y)) for node in nodes]
        if any(not math.isfinite(value) for point in points for value in point):
            findings.append({"contour": index, "kind": "nonfinite"})
            continue
        if not contour.closed:
            findings.append({"contour": index, "kind": "open"})
        elif (count := sum(bool(node.isOn()) for node in nodes)) < 3:
            findings.append({"contour": index, "kind": "few-on-curve", "count": count})
        ends = points[1:] + (points[:1] if contour.closed and len(points) > 1 else [])
        for number, (start, end) in enumerate(zip(points, ends), 1):
            if start == end:
                findings.append(
                    {
                        "contour": index,
                        "kind": "repeated-point",
                        "node": number,
                        "point": list(start),
                    }
                )
        if points:
            xs, ys = zip(*points)
            width, height = max(xs) - min(xs), max(ys) - min(ys)
            if width < threshold or height < threshold:
                findings.append(
                    {
                        "contour": index,
                        "kind": "small-extent",
                        "width": width,
                        "height": height,
                    }
                )
    return findings


class Scan:
    """Read glyphs by index in bounded UI-thread ticks, then verify identities.

    Each tick has its own cooperative deadline. A native getter cannot be
    interrupted, but the next glyph waits for another tick when time is up.
    No whole-font catalogue capture occurs before the timer starts.
    """

    def __init__(
        self,
        threshold: float,
        service: Any = None,
        native: Any = None,
        clock: Any = monotonic,
    ) -> None:
        if service is None:
            import fly.ap.scripting as service
        if native is None:
            from fly import fl as native
        diagnose([], threshold)
        self.service, self.native, self.clock = service, native, clock
        self.threshold = threshold
        package = service.current_package()
        if package is None:
            raise ValueError("Open a font first.")
        self.package_id, self.font_id = int(package.id), int(package.fgId)
        self.master = str(package.master)
        font = native.CurrentFont()
        if font is None or int(font.id) != self.font_id:
            raise ValueError("Current font changed; refresh the report.")
        self.total = len(font)
        self.index = 0
        self.checking = False
        self.facts: list[tuple[Any, ...]] = []
        self.problems: dict[str, Any] = {}
        self.missing: list[str] = []

    def context(self) -> tuple[Any, Any]:
        """Reacquire current objects each tick; do not use a closed package."""
        package = self.service.current_package(self.package_id)
        font = self.native.CurrentFont()
        if (
            package is None
            or font is None
            or int(font.id) != self.font_id
            or str(package.master) != self.master
            or len(font) != self.total
        ):
            raise ValueError("Current font or master changed; refresh the report.")
        return package, font

    def step(self) -> dict[str, Any] | None:
        """Return only a complete, verified report; None means more work."""
        if current_thread() is not main_thread():
            raise RuntimeError("Scan on the main UI thread.")
        package, font = self.context()
        deadline = self.clock() + STEP_SECONDS
        for processed in range(GLYPHS_PER_TICK):
            if self.index == self.total:
                break
            if processed and self.clock() >= deadline:
                break
            source = font[self.index]
            name = str(source.name)
            glyph = package.findName(name)
            if glyph is None:
                raise ValueError("Font glyphs changed; refresh the report.")
            fact = (int(source.id), name, glyph.lastModified.toMSecsSinceEpoch())
            if self.checking:
                if fact != self.facts[self.index]:
                    raise ValueError("Font glyphs changed; refresh the report.")
            else:
                self.facts.append(fact)
                layer = glyph.findLayer(self.master)
                if layer is None:
                    self.missing.append(name)
                elif found := diagnose(layer.getContours(), self.threshold):
                    self.problems[name] = found
            self.index += 1
        self.context()
        if self.index < self.total:
            return None
        if not self.checking:
            self.checking, self.index = True, 0
            return None
        return {
            "schema": 1,
            "package_id": self.package_id,
            "master": self.master,
            "min_extent": self.threshold,
            "glyphs_scanned": self.total,
            "missing_layers": self.missing,
            "problems": self.problems,
        }

    def progress(self) -> str:
        """Give an exact per-pass glyph count without exposing partial findings."""
        phase = "Checking" if self.checking else "Scanning"
        return f"{phase} {self.index} / {self.total} glyphs"


def report_text(report: dict[str, Any]) -> str:
    """Encode the complete report as ASCII JSON for lossless Qt display."""
    return json.dumps(report, ensure_ascii=True, allow_nan=False, indent=2) + "\n"


def export_report(filename: str, report: dict[str, Any]) -> None:
    """Write a captured report to a new absolute path; never overwrite."""
    if any(char in filename for char in ("\0", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("Filename contains text that Qt cannot preserve.")
    path = Path(filename).expanduser()
    if not path.is_absolute():
        raise ValueError("Enter an absolute path to a new JSON file.")
    content = report_text(report)
    with path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(content)


def show(qt: Any, parent: Any) -> Any:
    """Show a retained modeless panel with owned, guarded connections."""
    import fly.ap.draft_signals as signals

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Keep the complete report and disconnect signals before deletion."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(700, 520)
            self.stack = gui.QVBoxLayout(self)
            self.stack.setContentsMargins(16, 16, 16, 16)
            self.stack.setSpacing(8)
            self.status_line = gui.QLabel(
                "Refresh to inspect the current master.", self
            )
            self.stack.addWidget(self.status_line)
            self.progress_line = gui.QLabel("", self)
            self.stack.addWidget(self.progress_line)
            self.stack.addWidget(gui.QLabel("Minimum node extent (font units)", self))
            self.extent_control = gui.QDoubleSpinBox(self)
            self.extent_control.setRange(0, 1000000)
            self.extent_control.setDecimals(2)
            self.extent_control.setValue(4)
            self.stack.addWidget(self.extent_control)
            self.preview = gui.QPlainTextEdit(self)
            self.preview.setReadOnly(True)
            self.stack.addWidget(self.preview)
            self.stack.addWidget(gui.QLabel("New JSON file (absolute path)", self))
            self.destination = gui.QLineEdit(self)
            self.stack.addWidget(self.destination)
            self.scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )
            self.result: dict[str, Any] | None = None
            self.scan_work: Scan | None = None
            self.scan_timer = core.QTimer(self)
            self.scope.connect(self.scan_timer.timeout, lambda *args: self.scan_step())
            self.scope.connect(self.destroyed, lambda *args: self.release_owner())
            for label, action in (
                ("Refresh", self.refresh_report),
                ("Cancel", self.cancel_scan),
                ("Select glyphs with findings", self.select_findings),
                ("Export", self.save_report),
            ):
                button = gui.QPushButton(label, self)
                self.stack.addWidget(button)
                self.scope.connect(
                    button.clicked, lambda *args, action=action: action()
                )

        def cancel_scan(self) -> None:
            """Stop work and release every partial finding before returning."""
            self.scan_timer.stop()
            self.scan_work = None
            self.result = None
            self.preview.setPlainText("")
            self.progress_line.setText("Cancelled; no partial report kept.")

        def refresh_report(self) -> None:
            """Start an empty scan; native glyph reads happen on timer ticks."""
            self.cancel_scan()
            try:
                self.scan_work = Scan(float(self.extent_control.value))
                self.progress_line.setText(self.scan_work.progress())
                self.status_line.setText(
                    "Scanning the current master. Cancel discards this scan."
                )
                self.scan_timer.start(0)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(str(error))

        def scan_step(self) -> None:
            """Publish only when both scan and identity checks have finished."""
            if self.scan_work is None:
                return
            try:
                result = self.scan_work.step()
                self.progress_line.setText(self.scan_work.progress())
                if result is None:
                    return
                self.scan_timer.stop()
                self.preview.setPlainText(report_text(result))
                self.result = result
                self.scan_work = None
                count = sum(len(rows) for rows in result["problems"].values())
                self.status_line.setText(
                    f"{result['master']}: {count} findings; {result['glyphs_scanned']} glyphs scanned."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.cancel_scan()
                self.status_line.setText(str(error))

        def select_findings(self) -> None:
            """Delegate the Font-window guard and bound selection to App."""
            import fly.ap.scripting as scripting  # noqa: PLR0402 - preserve module imports

            try:
                if self.result is None:
                    raise ValueError("Finish a report first.")
                names = list(self.result["problems"])
                if not names:
                    raise ValueError("The report has no glyphs with findings.")
                selected = scripting.select_glyphs(
                    names, package_id=self.result["package_id"]
                )
                self.status_line.setText(
                    f"Selected {len(selected)} glyphs with findings."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(str(error))

        def save_report(self) -> None:
            """Export the labelled captured snapshot, including every finding."""
            try:
                if self.result is None:
                    raise ValueError("Refresh a report from an open font first.")
                export_report(str(self.destination.text), self.result)
                self.status_line.setText(
                    "Captured report exported; existing files are kept."
                )
            except (ValueError, RuntimeError, OSError) as error:
                self.status_line.setText(str(error))

        def release_owner(self) -> None:
            """Fence callbacks if FontLab destroys the parent window."""
            self.scan_work = None
            self.result = None
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Keep a failed disconnect available for a Close retry."""
            self.cancel_scan()
            if not self.scope.finish():
                event.ignore()
                return
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.refresh_report()
        panel.show()
    except Exception:
        panel.cancel_scan()
        if panel.scope.finish():
            _PANELS.remove(panel)
            panel.deleteLater()
        raise
    return panel


def main() -> None:
    """Use FontLab's existing application and main window."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
