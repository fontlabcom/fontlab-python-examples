# this_file: examples/pythonqt/live_glyph_panel.py
# SPDX-License-Identifier: Apache-2.0
"""What: A modeless tool panel with live information about the current glyph.
Shows: a QWidget tool window opened from a script, a QTimer that watches for a
glyph change, Qt properties read through one helper, and clean teardown.
Run: copy to a FontLab Scripts folder and run it from the Scripts menu, with a
font open. The panel stays open while you work; run the script again to
replace it. Close it with its title bar.
Setup: FontLab 9, Python 3.11, Fly with App (fly.ap.scripting). Nothing is
written to any font.

Why a timer: this example does not assume a glyph-change signal. Polling the
current glyph name every 200 ms is cheap, and the label is rewritten only when
the name differs, so the panel never flickers or fights the editor.
"""

from __future__ import annotations

from typing import Any

KEY = "pythonqt-example-live-glyph-panel"
POLL_MS = 200


def read(owner: Any, name: str) -> Any:
    """PythonQt exposes some members as properties and some as methods; accept both."""
    item = getattr(owner, name)
    return item() if callable(item) else item


def summary(glyph: Any) -> str:
    """Describe a glyph (or None) as text. Pure Python, so it is easy to test."""
    if glyph is None:
        return "No current glyph.\nOpen a glyph window or select a glyph."
    lines = [f"Name: {read(glyph, 'name')}"]
    layers = list(read(glyph, "layers") or ())
    lines.append(f"Layers: {len(layers)}")
    layer = read(glyph, "activeLayer")
    if layer is not None:
        lines.append(f"Active layer: {read(layer, 'name')}")
        lines.append(f"Advance width: {read(layer, 'advanceWidth')}")
    return "\n".join(lines)


def build(parent: Any) -> Any:
    """Build the panel. Qt is imported here so the module imports without FontLab."""
    from fly import fl, qt

    core, gui = qt.QtCore, qt.QtGui  # PythonQt has no QtWidgets: widgets live in QtGui.
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)  # A tool window floats above its parent, modeless.
    panel.setWindowTitle("Live Glyph Panel")
    panel.setAttribute(core.Qt.WA_DeleteOnClose)  # Closing frees the widget and its timer.
    label = gui.QLabel("", panel)
    label.setTextInteractionFlags(core.Qt.TextSelectableByMouse)
    layout = gui.QVBoxLayout(panel)
    layout.addWidget(label)
    shown = [object()]  # Never equals a glyph name, so the first tick always draws.

    def tick(*args: Any) -> None:
        # Slots run inside Qt: never let an exception escape into the event loop.
        try:
            glyph = fl.CurrentGlyph()
            name = None if glyph is None else read(glyph, "name")
            if name != shown[0]:
                shown[0] = name
                label.setText(summary(glyph))
        except Exception as error:  # noqa: BLE001 - Qt callback boundary
            label.setText(f"Refresh failed: {error}")

    # The timer is a child of the panel, so Qt deletes it with the panel.
    timer = core.QTimer(panel)
    timer.setInterval(POLL_MS)
    timer.timeout.connect(tick)  # Signal.connect(callable) is the PythonQt style.
    timer.start()
    tick()
    return panel


def main() -> Any:
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(build, KEY)


if __name__ == "__main__":
    main()
