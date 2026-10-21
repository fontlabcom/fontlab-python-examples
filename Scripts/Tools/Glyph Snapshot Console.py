# this_file: Scripts/Tools/Glyph Snapshot Console.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source: rescued/part2/ports/insights/timer-batch.py
# preserved-source-sha256: 9bede8e4486e03be3c182cd474084ab6a9200ca2419efb4ae3b2cc70ca78bfaa
# preserved-source: rescued/part2/ports/insights/owned-repl.py
# preserved-source-sha256: 3b5fb1184dd28f2caa23b1e90eb53308a0d77ead01f5a0bc4fd3cc62bf7d95df
"""Query current-font name, Unicode and modification data with trusted Python.

What: Evaluate short expressions or statements on detached glyph records.
How: Capture once on the UI thread with a glyph-count-scaled deadline and a
Scanning label (at most 120 seconds). Build the namespace once. No worker or conversion timer is used.
Why: Test report expressions without giving the query namespace native handles.
Usage: Capture, enter Python, then Run or press Return. For example,
[g['name'] for g in glyphs if not g['unicode']]. The unicode field is a string
such as "U+0041 U+00C1"; modified is "yyyy-MM-dd HH:mm:ss", or empty if unset.
Select output and copy to a script or report. Capture resets local variables.
Choose the query deadline: 5 seconds by default, at most 60 seconds. A Python
trace guard stops Python loops and restores the earlier host trace. A loop in
native code without Python line events cannot be stopped by this guard.
Code that catches every exception can outlive the time limit.
Benefit: Experiment with real glyph data and keep complete query results.
This runs trusted code in the host process, not a security sandbox. User code
can change detached data. The panel itself calls no font writer.
Setup: FontLab 9, Python 3.11, Fly and App glyph_catalog/draft_signals/scripting.
Independent rewrite of timer-batch and owned-repl.
Based on the author's own FontLab sample, Apache-2.0.
No original source body is redistributed.
"""

import sys
from contextlib import redirect_stdout
from io import StringIO
from time import monotonic
from typing import Any

TITLE = "Glyph Snapshot Console"
HELP = "Capture current-font data, then query glyphs (name, unicode, modified). Copy results with Cmd+C. Code that catches every exception can outlive the time limit."


FIELDS = ("name", "unicode", "modified")
BUILTINS = {function.__name__: function for function in (
    len, sum, min, max, sorted, str, int, float, round, set, list, dict, tuple,
    any, all, enumerate, zip, range, bool, abs, isinstance, print,
)}


def capture_current(status_line: Any) -> Any:
    """Scale the scan budget up to 120 seconds; never reject a font by size."""
    import fly.ap.glyph_catalog as catalog
    import fly.ap.qt_properties as properties
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires the module alias

    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font before scanning.")
    count = int(properties.value(package, "glyphsCount"))
    budget = min(120.0, 10.0 + 0.02 * count)
    status_line.setText(f"Scanning {count:,} glyphs (budget {budget:g} s)…")
    status_line.repaint()
    return catalog.capture(deadline=monotonic() + budget)


def snapshot_namespace(rows: tuple[tuple[str, str, str], ...]) -> dict[str, Any]:
    """Build one detached namespace; reuse the single built-in dictionary."""
    return {"glyphs": [dict(zip(FIELDS, row)) for row in rows], "__builtins__": BUILTINS}


def evaluate(source: str, namespace: dict[str, Any], seconds: float = 5.0) -> str:
    """Bound trusted Python execution; chain global/local traces and restore both."""
    if not 0 < seconds <= 60:
        raise ValueError("Choose a query deadline greater than 0 and at most 60 seconds.")
    previous = sys.gettrace()
    if previous is not None and not callable(previous):
        # Refuse an opaque trace object; None permits normal untraced panel slots.
        raise RuntimeError("Time limit unavailable: FontLab already traces this call")
    deadline = monotonic() + seconds
    query_frames: dict[Any, bool] = {}

    def check() -> None:
        if monotonic() >= deadline:
            raise TimeoutError(f"Query exceeded {seconds:g} seconds.")

    def guard(frame: Any, event: str, arg: Any) -> Any:
        earlier = previous(frame, event, arg) if previous is not None else None
        watched = frame.f_code.co_filename == "<glyph-snapshot>"
        previous_opcodes = frame.f_trace_opcodes
        if watched:
            previous_opcodes = query_frames.setdefault(frame, previous_opcodes)
            frame.f_trace_opcodes = True  # Single-line loops can have no further line events.
            check()

        def local_trace(frame: Any, event: str, arg: Any) -> Any:
            nonlocal earlier
            if earlier is not None and (event != "opcode" or previous_opcodes):
                earlier = earlier(frame, event, arg)
            if watched:
                frame.f_trace_opcodes = True
                check()
            return local_trace

        return local_trace

    output = StringIO()
    try:
        sys.settrace(guard)
        with redirect_stdout(output):
            try:
                compiled = compile(source, "<glyph-snapshot>", "eval")
            except SyntaxError:
                exec(compile(source, "<glyph-snapshot>", "exec"), namespace)  # noqa: S102 - trusted console
                result = "" if output.tell() else "Statement complete."
            else:
                value = eval(compiled, namespace)
                result = "" if value is None and output.tell() else repr(value)
            check()
            return output.getvalue() + result
    finally:
        try:
            for frame, flag in query_frames.items():
                frame.f_trace_opcodes = flag
        finally:
            sys.settrace(previous)
            query_frames.clear()


_PANELS: list[Any] = []


def show(qt: Any, parent: Any) -> Any:
    """Open an owned tool window; use App to fence and disconnect callbacks."""
    import fly.ap.draft_signals as signals

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Keep controls and callback references until native cleanup succeeds."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(700, 500)
            self.box = gui.QVBoxLayout(self)
            self.box.setContentsMargins(16, 16, 16, 16)
            self.box.setSpacing(8)
            self.status_line = gui.QLabel(HELP, self)
            self.status_line.setWordWrap(True)
            self.box.addWidget(self.status_line)
            self.scope = signals.Scope(lambda error: self.status_line.setText(str(error)))
            self.scope.connect(self.destroyed, lambda *args: self.release_owner())

        def add_button(self, text: str, action: Any) -> None:
            """Wrap signal arguments; never connect a native slot directly."""
            button = gui.QPushButton(text, self)
            self.box.addWidget(button)
            self.scope.connect(button.clicked, lambda *args: action())

        def release_owner(self) -> None:
            """Drop Python references when FontLab destroys the native parent."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Stop owned work and disconnect before scheduling native deletion."""
            self.stop_owned()
            if not self.scope.finish():
                event.ignore()
                return
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

        def stop_owned(self) -> None:
            """Discard the detached query data; no timer remains to stop."""
            self.query_namespace = None

        def capture_rows(self) -> None:
            """Replace old output with one complete current-font snapshot."""
            self.stop_owned()
            self.output_box.setPlainText("")
            self.query_namespace = snapshot_namespace(tuple(capture_current(self.status_line).rows))
            count = len(self.query_namespace["glyphs"])
            self.status_line.setText(f"Ready: {count} glyphs. Capture resets variables.")

        def stop_query(self) -> None:
            """Discard the snapshot; query execution has its own trace deadline."""
            self.stop_owned()
            self.output_box.setPlainText("")
            self.status_line.setText("Snapshot cleared. Capture again before Run.")

        def run_query(self) -> None:
            """Show Python failures, including a deadline timeout, in the output."""
            import fly.ap.qt_properties as properties

            self.output_box.setPlainText("")
            try:
                if self.query_namespace is None:
                    raise ValueError("Capture before Run.")
                source = str(properties.value(self.query_entry, "text"))
                seconds = float(properties.value(self.deadline_control, "value"))
                result = evaluate(source, self.query_namespace, seconds)
            except Exception as error:  # noqa: BLE001 - trusted console boundary
                self.output_box.setPlainText(f"{type(error).__name__}: {error}")
                self.status_line.setText("Query failed. Correct the input or adjust its deadline.")
                return
            self.output_box.setPlainText(result)
            self.status_line.setText("Result from the captured snapshot. Capture after font edits.")

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.query_namespace = None
        panel.box.addWidget(gui.QLabel("Query deadline (seconds; Python events only)", panel))
        panel.deadline_control = gui.QDoubleSpinBox(panel)
        panel.deadline_control.setRange(0.01, 60.0)
        panel.deadline_control.setValue(5.0)
        panel.box.addWidget(panel.deadline_control)
        panel.query_entry = gui.QLineEdit(panel)
        panel.query_entry.setText("len(glyphs)")
        panel.scope.connect(panel.query_entry.returnPressed, lambda *args: panel.run_query())
        panel.box.addWidget(panel.query_entry)
        panel.output_box = gui.QPlainTextEdit(panel)
        panel.output_box.setReadOnly(True)
        panel.box.addWidget(panel.output_box)
        panel.add_button("Capture / Reset Namespace", panel.capture_rows)
        panel.add_button("Run Trusted Python", panel.run_query)
        panel.add_button("Clear Snapshot", panel.stop_query)
        panel.show()
    except Exception:
        panel.stop_owned()
        if panel.scope.finish():
            _PANELS.remove(panel)
            panel.deleteLater()
        else:
            panel.show()
        raise
    return panel


def main() -> None:
    """Resolve the running FontLab window lazily; never create an application."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError, AttributeError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
