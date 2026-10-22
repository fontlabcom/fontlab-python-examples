# this_file: Scripts/Tools/Layer Metric Comparison.py
# SPDX-License-Identifier: Apache-2.0
"""What: Compare selected glyph-layer measurements with one reference cell.
How: Read complete equal passes of advances, outline bounds and sidebearings.
Calculate signed differences or percentages. Zero denominators stay undefined;
empty outlines keep unavailable dimensions and margins. Never substitute one.
Why: Relative measurements expose proportion and spacing differences directly.
Usage: Select layers in a Font or Glyph window. Choose Advance, Width, Height,
Left or Right. Enter a reference glyph and layer, or leave both blank to use
the first selected occurrence. Choose Difference or Percent. Copy the table.
Benefit: Compare actual selected layers without switching the active master.
The table is tab-separated text. Selection controls the compared layers;
this tool does not add unselected masters, scan named glyph lists or provide
an independent selected-node part/whole calculator.
View > Metrics Table edits metrics; this comparison reports relative values.

Independent behaviour-only rewrite of the metric-comparison idea from Stats.py.
Credit: Vassil Kateliev and Karandash Type Foundry; kateliev/TypeRig, MPL-2.0.
No TypeRig code, comments, icons or resources are included.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.
"""

from math import isfinite
from threading import current_thread, main_thread
from time import monotonic
from typing import Any

TITLE = "Layer Metric Comparison"
HELP = "Select glyph layers. Blank reference fields use the first occurrence."
FIELDS = (
    ("Measurement: Advance, Width, Height, Left or Right", "Advance"),
    ("Reference glyph", ""),
    ("Reference layer", ""),
    ("Mode: Difference or Percent", "Difference"),
)
CHOICES: dict[int, tuple[str, ...]] = {
    0: ("Advance", "Width", "Height", "Left", "Right"),
    3: ("Difference", "Percent"),
}
_PANELS: list[Any] = []


MetricRow = tuple[
    str, str, float, float | None, float | None, float | None, float | None
]


def read_rows(selected: Any, deadline: float) -> tuple[MetricRow, ...]:
    """Read scalar geometry only; retain empty outlines as unavailable values."""
    import fly.ap.qt_properties as properties

    rows = []
    for item in selected.occurrences:
        if monotonic() >= deadline:
            raise TimeoutError("Metric scan expired; no partial result.")
        name, layer_name = checked(item.glyph_name), checked(item.layer_name)
        if any(char in name + layer_name for char in "\t\n"):
            raise ValueError("Glyph or layer name cannot form a TSV cell.")
        advance = float(properties.value(item.layer, "advanceWidth"))
        width = height = left = right = None
        if int(properties.value(item.layer, "shapesCount")):
            bounds = properties.value(item.layer, "boundingBox")
            if not properties.value(bounds, "isNull") and not properties.value(
                bounds, "isEmpty"
            ):
                width = float(properties.value(bounds, "width"))
                height = float(properties.value(bounds, "height"))
                left = float(properties.value(bounds, "x"))
                right = advance - left - width
        values = (advance, width, height, left, right)
        if any(value is not None and not isfinite(value) for value in values):
            raise ValueError(f"Measurements must be finite: {name} / {layer_name}.")
        rows.append((name, layer_name, *values))
    return tuple(rows)


def capture_metrics() -> tuple[MetricRow, ...]:
    """Use ordered selected-layer captures with equal scalar reads and context."""
    import fly.ap.layer_selection as selection

    if current_thread() is not main_thread():
        raise RuntimeError("Read layer metrics on the main UI thread.")
    deadline = monotonic() + 2.0
    first = selection.capture(deadline)
    rows = read_rows(first, deadline)
    second = selection.capture(deadline)
    other = read_rows(second, deadline)
    final = selection.capture(deadline)
    if monotonic() >= deadline:
        raise TimeoutError("Metric scan expired; no partial result.")
    if first != second or second != final or rows != other:
        raise ValueError("Selected layers or measurements changed; refresh again.")
    if not rows:
        raise ValueError("Select at least one glyph layer first.")
    return rows


def build_output(fields: tuple[str, ...]) -> str:
    """Compare every occurrence to an explicit reference; preserve real zeros."""
    measurement, glyph_name, layer_name, mode = fields
    labels = ("Advance", "Width", "Height", "Left", "Right")
    if measurement not in labels or mode not in ("Difference", "Percent"):
        raise ValueError("Choose a listed measurement and Difference or Percent.")
    rows = capture_metrics()
    if bool(glyph_name) != bool(layer_name):
        raise ValueError("Enter both reference names or leave both blank.")
    reference = (
        rows[0]
        if not glyph_name
        else next((row for row in rows if row[:2] == (glyph_name, layer_name)), None)
    )
    if reference is None:
        raise ValueError("The reference glyph and layer must be selected.")
    index = labels.index(measurement) + 2
    base = reference[index]
    lines = ["Glyph\tLayer\tValue\tCompared"]
    for row in rows:
        value = row[index]
        compared = "Unavailable"
        if value is not None and base is not None:
            if mode == "Difference":
                result = value - base
            elif base == 0:
                result = None
                compared = "Undefined (zero reference)"
            else:
                result = value / base * 100
            if result is not None:
                if not isfinite(result):
                    raise ValueError("Compared measurement must be finite.")
                compared = f"{result:g}"
        text = "Unavailable" if value is None else f"{value:g}"
        lines.append(f"{row[0]}\t{row[1]}\t{text}\t{compared}")
    return "\n".join(lines)


def checked(text: str) -> str:
    """Refuse characters that the Qt bridge or proof syntax can change."""
    if any(char in text for char in ("\0", "\u00a0", "\u2028", "\u2029", "\r")):
        raise ValueError("Text contains NUL, NBSP, CR or a Unicode line separator.")
    try:
        text.encode("utf-8")
    except UnicodeError as error:
        raise ValueError("Text contains an invalid Unicode surrogate.") from error
    return text


def show(qt: Any, parent: Any) -> Any:
    """Open an owned modeless panel; drain callbacks before deletion."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own inputs, current output and a retryable signal scope."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(740, 540)
            self.stack_box = gui.QVBoxLayout(self)
            self.status_line = gui.QLabel(HELP, self)
            self.stack_box.addWidget(self.status_line)
            self.signal_scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )

        def build_controls(self) -> None:
            """Build fallible controls under the outer owned-window cleanup guard."""
            self.input_boxes: list[Any] = []
            for index, (label, initial) in enumerate(FIELDS):
                self.stack_box.addWidget(gui.QLabel(label, self))
                if index in CHOICES:
                    item = gui.QComboBox(self)
                    item.addItems(list(CHOICES[index]))
                    item.setCurrentIndex(CHOICES[index].index(initial))
                else:
                    item = gui.QLineEdit(self)
                    item.setText(initial)
                self.stack_box.addWidget(item)
                self.input_boxes.append(item)
            self.output_box = gui.QPlainTextEdit(self)
            self.output_box.setReadOnly(True)
            self.stack_box.addWidget(self.output_box)
            for label, action in (
                ("Refresh Result", self.refresh_output),
                ("Copy Fresh Result", self.copy_output),
            ):
                button = gui.QPushButton(label, self)
                self.stack_box.addWidget(button)
                self.signal_scope.connect(
                    button.clicked, lambda *args, call=action: call()
                )
            self.signal_scope.connect(
                self.destroyed, lambda *args: self.release_owner()
            )

        def fresh_output(self) -> str:
            """Recapture live input; never export a previous font's result."""
            fields = tuple(
                checked(
                    str(
                        properties.value(
                            item, "currentText" if index in CHOICES else "text"
                        )
                    )
                )
                for index, item in enumerate(self.input_boxes)
            )
            return checked(build_output(fields))

        def refresh_output(self) -> None:
            """Replace the result atomically; clear stale output after a refusal."""
            try:
                text = self.fresh_output()
                self.output_box.setPlainText(text)
                self.status_line.setText("Result refreshed. " + HELP)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output_box.setPlainText("")
                self.status_line.setText(str(error))

        def copy_output(self) -> None:
            """Read again before copying a FontLab-consumable proof or table."""
            try:
                text = self.fresh_output()
                if not text:
                    raise ValueError("No matching output to copy.")
                gui.QApplication.clipboard().setText(text)
                self.output_box.setPlainText(text)
                self.status_line.setText("Fresh result copied.")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output_box.setPlainText("")
                self.status_line.setText(str(error))

        def release_owner(self) -> None:
            """Release Python state when the native parent destroys this panel."""
            self.signal_scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Retain failed disconnections for a window-Close retry."""
            if not self.signal_scope.finish():
                event.ignore()
                return
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.build_controls()
        panel.refresh_output()
        panel.show()
    except Exception:
        if panel.signal_scope.finish():
            _PANELS.remove(panel)
            panel.deleteLater()
        raise
    return panel


def main() -> None:
    """Open inside FontLab's existing application and main window."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
