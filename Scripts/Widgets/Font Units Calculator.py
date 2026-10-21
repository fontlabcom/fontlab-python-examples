# this_file: Scripts/Widgets/Font Units Calculator.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/calculator-356e4e807f1e789f.py
# preserved-source-sha256: e598d62c5dd2e7d33560b03ddc41121da3afa6e6b6c86e1a74ff930f75b6fa2b
# preserved-source: rescued/part2/ports/widgets/pyqt-official/calculator-356e4e807f1e789f.py
# preserved-source-sha256: c85c69f307812c61f0108ad203a029d9513470b737af9c06c65d1d76e6befecc
"""What: Calculate font-unit values and their em and point equivalents.
How: Read the current font UPM on each Calculate. Apply one explicit operation.
Why: Keep unit arithmetic separate from stored glyph metrics.
Usage: Enter A, an operation and B. Set the proof size in points. Calculate,
then select and copy the result. No expression evaluation or font writes.
Benefit: Transfer measured values into spacing and proof-size decisions.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Calculator example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.
"""

import math
import operator
from typing import Any


def calculate(
    a: float, operation: str, b: float, upm: float, points: float
) -> tuple[float, float, float]:
    """Return units, em fraction and points. Refuse invalid or infinite results."""
    if (
        not all(math.isfinite(v) for v in (a, b, upm, points))
        or upm <= 0
        or points <= 0
    ):
        raise ValueError("Use finite numbers, positive UPM and a positive point size.")
    operations = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }
    if operation not in operations or (operation == "/" and b == 0):
        raise ValueError("Choose +, -, * or /; division by zero is refused.")
    units = operations[operation](a, b)
    result = (units, units / upm, units / upm * points)
    if not all(math.isfinite(v) for v in result):
        raise ValueError("Result exceeds the finite numeric range.")
    return result


def main() -> Any:
    """Open the owned modeless App panel. Import Qt only in the host."""
    import fly.ap.qt_properties as properties
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module imports
    from fly import qt

    g = qt.QtGui
    base = scripting.names_dialog_type()

    class Dialog(base):
        """Keep arithmetic inputs and current-font unit results together."""

        def __init__(self, parent: Any) -> None:
            """Build labelled controls with a selectable plain-text result."""
            base.__init__(
                self, parent, "Font Units Calculator", "widgets_font_units_calculator"
            )
            self.subtitle.setText(
                "Calculate units, ems and points using the current font UPM."
            )
            self.amount, self.operand, self.point_size = (
                g.QDoubleSpinBox(),
                g.QDoubleSpinBox(),
                g.QDoubleSpinBox(),
            )
            self.operation = g.QComboBox()
            self.operation.addItems(["+", "-", "*", "/"])
            for label, control, default in (
                ("A (font units)", self.amount, 500),
                ("B (units for +/-, factor for */)", self.operand, 20),
                ("Proof size (points)", self.point_size, 12),
            ):
                control.setRange(-1000000, 1000000)
                control.setDecimals(4)
                control.setValue(default)
                self.root.addWidget(g.QLabel(label))
                self.root.addWidget(control)
            self.root.addWidget(self.operation)
            self.output = g.QPlainTextEdit()
            self.output.setReadOnly(True)
            self.status = g.QLabel(
                "Enter values, then Calculate using the current font UPM."
            )
            self.status.setTextFormat(qt.QtCore.Qt.PlainText)
            self.status.setWordWrap(True)
            self.root.addWidget(self.output)
            self.preview_button, self.close_button = (
                g.QPushButton("Calculate"),
                g.QPushButton("Close"),
            )
            for control in (self.preview_button, self.status, self.close_button):
                self.root.addWidget(control)
            self._connect(self.preview_button.clicked, lambda *args: self.preview())
            self._connect(self.close_button.clicked, lambda *args: self.close())
            self.resize(620, 580)

        def publish(self, text: str) -> None:
            """Publish exact result text; refuse Qt character conversion."""
            if any(c in text for c in ("\x00", "\u00a0", "\u2028", "\u2029", "\r")):
                raise ValueError(
                    "Result contains characters Qt cannot preserve exactly."
                )
            self.output.setPlainText(text)
            if str(self.output.toPlainText()) != text:
                self.output.setPlainText("")
                raise ValueError("Qt changed the result text; copy refused.")

        def preview(self) -> None:
            """Calculate with current UPM; clear failed arithmetic or font reads."""
            self.status.setText("Calculating with current-font UPM...")
            self.output.setPlainText("")
            try:
                self.build_result()
                self.status.setText("Result ready. Select text and Copy.")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output.setPlainText("")
                self.status.setText(str(error))

        def build_result(self) -> None:
            """Build one complete result from current controls and context."""
            package = scripting.current_package()
            if package is None:
                raise ValueError("Open a font before calculating font units.")
            identity, upm = package.id, float(package.upm)
            units, ems, points = calculate(
                float(properties.value(self.amount, "value")),
                str(properties.value(self.operation, "currentText")),
                float(properties.value(self.operand, "value")),
                upm,
                float(properties.value(self.point_size, "value")),
            )
            current = scripting.current_package(identity)
            if current is None or float(current.upm) != upm:
                raise ValueError("Font or UPM changed; calculate again.")
            self.publish(
                f"UPM: {upm:g}\nUnits: {units:g}\nEm: {ems:g}\nPoints: {points:g}"
            )

    return scripting.show_script_dialog(Dialog, "widgets_font_units_calculator")


if __name__ == "__main__":
    main()
