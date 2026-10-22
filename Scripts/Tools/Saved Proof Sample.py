# this_file: Scripts/Tools/Saved Proof Sample.py
# SPDX-License-Identifier: Apache-2.0
# historical source: rescued/part2/ports/insights/sandbox-settings.py
# historical source sha256: a3dacffc45c2c5e1d1bc83b1a5b672c20db9a3873d0cc98166515ed96d1fd8bb
"""Keep a reusable proof sample and check it against the current font.

What: Save one proof string in an isolated example settings namespace.
How: QSettings stores only proof/sample. Check Coverage reads the full current
font catalogue with a glyph-count-scaled scan deadline capped at 120 seconds
and a Scanning label.
It reports covered and missing Unicode scalars as JSON.
Why: Persist a personal proof across launches and fonts in this tool's own
settings namespace. Coverage and clipboard output make that saved proof useful.
Usage: Edit the sample, Save Sample, Check Coverage, or Copy Proof Text to paste
in FontLab. Reset Saved Sample removes only this tool's key. Unsaved typing is
not persisted; Save Sample is explicit. Coverage always captures the font again.
Benefit: Keep a stable personal proof and compare encoding coverage across fonts.
No font or selection changes occur. Unicode coverage is not shaping coverage.
NUL and input-method transfer have known loss (fl#8567, fl#8568). This example
also conservatively refuses NBSP, U+2028/U+2029 and lone surrogates; it requires
exact proof text. This is a transfer policy, not a Unicode coverage limitation.
Setup: FontLab 9, Python 3.11, Fly, App glyph_catalog and draft_signals.
Independent rewrite of sandbox-settings.
Based on the author's own FontLab sample, Apache-2.0. No original source body is redistributed.
"""

import json
from time import monotonic
from typing import Any

TITLE = "Saved Proof Sample"
HELP = "Save a reusable proof, check the current font's Unicode coverage, or copy proof text."
DEFAULT = "Hamburgefontsiv"
SETTINGS_ORGANIZATION = "FontLabPythonExamples"
SETTINGS_APPLICATION = "SavedProofSample"


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


def checked(text: str) -> str:
    """Apply the conservative exact-transfer policy; do not assert native proof."""
    if any(char in text for char in ("\0", "\u00a0", "\u2028", "\u2029")) or any(
        0xD800 <= ord(char) <= 0xDFFF for char in text
    ):
        raise ValueError("Use text without NUL, NBSP, line separators or lone surrogates.")
    return text


def coverage_report(sample: str, rows: tuple[tuple[str, str, str], ...]) -> str:
    """Compare literal proof scalars with all Unicode assignments; return JSON."""
    needed = set(map(ord, checked(sample)))
    encoded = {int(token.removeprefix("U+"), 16) for _, codes, _ in rows for token in codes.split()}
    return json.dumps({"sample": sample, "glyph_count": len(rows),
                       "missing": [f"U+{point:04X}" for point in sorted(needed - encoded)],
                       "covered": [f"U+{point:04X}" for point in sorted(needed & encoded)]},
                      ensure_ascii=True, indent=2)


def persist_sample(settings: Any, sample: str | None, no_error: object) -> None:
    """Save or remove only the owned key; confirm QSettings sync status."""
    if sample is None:
        settings.remove("proof/sample")
    else:
        settings.setValue("proof/sample", checked(sample))
    settings.sync()
    if settings.status() != no_error:
        raise RuntimeError("Settings write failed. The sample may not persist; retry Save.")



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
            """There is no queued work in this panel."""

        def sample_text(self) -> str:
            """Read a known PythonQt text value and reject lossy characters."""
            import fly.ap.qt_properties as properties

            return checked(str(properties.value(self.sample_entry, "text")))

        def save_sample(self) -> None:
            """Persist the sample in this example's namespace only."""
            persist_sample(self.sample_settings, self.sample_text(), core.QSettings.NoError)
            self.status_line.setText("Sample saved for the next launch.")

        def reset_sample(self) -> None:
            """Remove one owned setting; leave other applications untouched."""
            persist_sample(self.sample_settings, None, core.QSettings.NoError)
            self.sample_entry.setText(DEFAULT)
            self.output_box.setPlainText("")
            self.status_line.setText("Saved sample reset.")

        def check_coverage(self) -> None:
            """Clear stale results before a fresh, complete FontLab capture."""
            self.output_box.setPlainText("")
            sample = self.sample_text()
            report = coverage_report(sample, tuple(capture_current(self.status_line).rows))
            self.output_box.setPlainText(report)
            self.status_line.setText("Coverage at the last check. Copy JSON with Cmd+C.")

        def copy_sample(self) -> None:
            """Put literal proof text on the clipboard for a FontLab text field."""
            gui.QApplication.clipboard().setText(self.sample_text())
            self.status_line.setText("Proof copied. Paste into a FontLab text field.")

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.sample_settings = core.QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION, panel)
        panel.sample_settings.setFallbacksEnabled(False)
        panel.sample_entry = gui.QLineEdit(panel)
        stored = str(panel.sample_settings.value("proof/sample", DEFAULT))
        try:
            sample = checked(stored)
        except ValueError:
            sample = DEFAULT
            panel.status_line.setText(
                "The saved sample is unusable. Edit the replacement and Save Sample, or Reset Saved Sample."
            )
        panel.sample_entry.setText(sample)
        if panel.sample_settings.status() != core.QSettings.NoError:
            raise RuntimeError("Cannot read the saved proof sample settings.")
        panel.box.addWidget(panel.sample_entry)
        panel.output_box = gui.QPlainTextEdit(panel)
        panel.output_box.setReadOnly(True)
        panel.box.addWidget(panel.output_box)
        panel.add_button("Save Sample", panel.save_sample)
        panel.add_button("Reset Saved Sample", panel.reset_sample)
        panel.add_button("Check Coverage", panel.check_coverage)
        panel.add_button("Copy Proof Text", panel.copy_sample)
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
