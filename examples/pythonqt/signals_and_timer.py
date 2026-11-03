# this_file: examples/pythonqt/signals_and_timer.py
# SPDX-License-Identifier: Apache-2.0
"""What: A small stopwatch panel that wires signals to slots three ways.
Shows: Signal.connect(callable) for a QTimer, the string form
button.connect("clicked()", slot) that PythonQt also provides, a wrapper that
swallows signal arguments, a single-shot QTimer, and a best-effort teardown
when the panel is destroyed.
Run: run from the Scripts menu. Start/Stop controls a 100 ms timer; Reset
zeroes it; the panel reports a "done" message from a single-shot timer after
5 seconds of running time. No font is needed and nothing is written.
Setup: FontLab 9, Python 3.11, Fly with App (fly.ap.scripting).

Rules from the host notes: bind what a slot needs in the closure instead of
calling self.sender(); disconnect what you connected before deleting widgets;
never let a slot raise into Qt.
"""

from __future__ import annotations

from typing import Any

KEY = "pythonqt-example-signals-and-timer"
TICK_MS = 100
DONE_AFTER_TICKS = 50


class Stopwatch:
    """Pure-Python state, separate from Qt so it can be tested without FontLab."""

    def __init__(self) -> None:
        self.ticks = 0
        self.running = False

    def tick(self) -> bool:
        """Advance one tick; True exactly when the done threshold is reached."""
        if not self.running:
            return False
        self.ticks += 1
        return self.ticks == DONE_AFTER_TICKS

    def text(self) -> str:
        seconds, tenths = divmod(self.ticks, 10)
        return f"{seconds}.{tenths} s"


def build(parent: Any) -> Any:
    from fly import qt

    core, gui = qt.QtCore, qt.QtGui
    state = Stopwatch()
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)
    panel.setWindowTitle("Signals and Timer")
    panel.setAttribute(core.Qt.WA_DeleteOnClose)
    display, status = gui.QLabel("0.0 s", panel), gui.QLabel("Stopped", panel)
    start, reset = gui.QPushButton("Start", panel), gui.QPushButton("Reset", panel)
    layout = gui.QVBoxLayout(panel)
    for widget in (display, status, start, reset):
        layout.addWidget(widget)
    timer = core.QTimer(panel)
    timer.setInterval(TICK_MS)

    def on_tick(*args: Any) -> None:
        try:
            if state.tick():
                # singleShot(0, ...) runs after the current slot returns.
                core.QTimer.singleShot(0, lambda: status.setText("Done: 5 seconds counted"))
            display.setText(state.text())
        except Exception as error:  # noqa: BLE001 - Qt callback boundary
            status.setText(f"Error: {error}")

    def on_start(*args: Any) -> None:
        # The closure already holds `start` and `state`: no self.sender() needed.
        state.running = not state.running
        start.setText("Stop" if state.running else "Start")
        status.setText("Running" if state.running else "Stopped")
        timer.start() if state.running else timer.stop()

    def on_reset(*args: Any) -> None:
        state.ticks = 0
        display.setText(state.text())

    timer.timeout.connect(on_tick)            # Style 1: attribute signal, callable slot.
    start.connect("clicked()", on_start)      # Style 2: signature string; extra args are dropped.
    reset.clicked.connect(on_reset)           # Style 1 again; the bool `checked` arrives in *args.

    def teardown(*args: Any) -> None:
        # Best effort: by now Qt may already have deleted the children, which
        # raises RuntimeError. The timer is parented to the panel, so Qt cleans up anyway.
        try:
            timer.stop()
            timer.timeout.disconnect(on_tick)
            reset.clicked.disconnect(on_reset)
        except RuntimeError:
            pass

    panel.destroyed.connect(teardown)
    return panel


def main() -> Any:
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(build, KEY)


if __name__ == "__main__":
    main()
