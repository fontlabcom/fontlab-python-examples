# this_file: examples/pythonqt/batch_with_progress.py
# SPDX-License-Identifier: Apache-2.0
"""What: Run a batch over every glyph of the current font with a cancellable
progress dialog, working on a copy of the data so the font is never changed.
Shows: QProgressDialog, chunked work driven by a zero-delay QTimer so the
interface stays responsive and the five-second script deadline is respected,
cancellation, and a result report.
Run: open a font and run from the Scripts menu. The batch reads each glyph's
advance width (fgGlyph.width) into a copy and computes widths scaled by 110 percent; it
reports the copy, and writes nothing to the font. Press Cancel to stop early.
Setup: FontLab 9, Python 3.11, Fly with App (fly.ap.scripting).

The pattern to copy: snapshot first (plain Python values), process the
snapshot in small slices, and show the result for review before any real edit.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

KEY = "pythonqt-example-batch-progress"
SCALE = 1.10
SLICE = 25  # Glyphs per timer tick: small enough that one tick never blocks the UI.


def snapshot(font: Any) -> list[tuple[str, float]]:
    """Copy (name, advance) for every glyph. After this the font is not touched."""
    result = []
    for glyph in font.glyphs:
        result.append((str(glyph.name), float(glyph.width)))
    return result


def process(records: list[tuple[str, float]], scale: float = SCALE) -> Iterator[tuple[str, float]]:
    """Yield (name, new advance) one glyph at a time; a generator keeps the work resumable."""
    for name, advance in records:
        yield name, round(advance * scale)


def build(parent: Any) -> Any:
    from fly import fl, qt

    font = fl.CurrentFont()
    if font is None:
        raise RuntimeError("Open a font first.")
    core, gui = qt.QtCore, qt.QtGui
    records = snapshot(font)
    work = process(records)
    done: list[tuple[str, float]] = []
    dialog = gui.QProgressDialog("Scaling widths on a copy...", "Cancel", 0, len(records), parent)
    dialog.setWindowTitle("Batch with Progress")
    dialog.setAttribute(core.Qt.WA_DeleteOnClose)
    dialog.setMinimumDuration(0)
    timer = core.QTimer(dialog)  # Child of the dialog: it dies with it.

    def finish(text: str) -> None:
        timer.stop()
        dialog.setLabelText(text)
        dialog.setCancelButtonText("Close")

    def step(*args: Any) -> None:
        try:
            for _ in range(SLICE):
                item = next(work, None)
                if item is None:
                    finish(f"Done: {len(done)} widths computed. The font was not changed.")
                    dialog.setValue(len(records))
                    return
                done.append(item)
            dialog.setValue(len(done))
        except Exception as error:  # noqa: BLE001 - Qt callback boundary
            finish(f"Stopped: {error}")

    def cancelled(*args: Any) -> None:
        timer.stop()
        # QProgressDialog also emits canceled when it is closed after finishing.
        message = "Batch cancelled after {} of {} glyphs" if len(done) < len(records) else "Batch dialog closed ({} of {} glyphs done)"
        print(message.format(len(done), len(records)) + "; the font was not changed.")

    dialog.canceled.connect(cancelled)  # Qt spells the signal "canceled".
    timer.timeout.connect(step)
    timer.start(0)  # Zero delay: run again as soon as the event loop is idle.
    return dialog


def main() -> Any:
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(build, KEY)


if __name__ == "__main__":
    main()
