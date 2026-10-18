# this_file: lessons/src/fontlab_python_lessons/form_dialog.py
# SPDX-License-Identifier: Apache-2.0
"""Teach Designer loading with real glyph metrics and a strictly local preview."""
from typing import Any

from fly import qt
from fly.ap import scripting as api

from ._dialog import LessonDialog
from .domain import Snapshot, capture, ensure_current, preview
from .forms import load_form


class GlyphMetricsForm(LessonDialog):
    """Load a packaged form; compare a hypothetical width without editing fonts."""

    def __init__(self, parent: Any = None) -> None:
        LessonDialog.__init__(self, parent, "Glyph Metrics Form", "glyph-metrics-form")
        self.subtitle.setText("Read actual current-master metrics. Preview only compares a hypothetical advance; it never applies an edit.")
        self.start(self.build)

    def build(self) -> None:
        """Keep controls on the Python subclass, never on native widget wrappers."""
        self.form, controls = load_form(qt, self)
        self.content.addWidget(self.form)
        self.glyph_name = controls["glyphName"]
        self.actual_advance = controls["actualAdvance"]
        self.actual_lsb = controls["actualLsb"]
        self.advance_box = controls["advanceBox"]
        self.preview_button = controls["previewButton"]
        self.result_label = controls["resultLabel"]
        self._connect(self.preview_button.clicked, lambda *args: self.preview())
        self._connect(self.glyph_name.currentIndexChanged, lambda *args: self.choose())

    def refresh(self) -> None:
        """Explicitly adopt the current font, master and ordered glyph names."""
        self.invalidate()
        scanned = capture(api, "form")
        blocked = self.glyph_name.blockSignals(True)
        try:
            self.glyph_name.clear()
            self.glyph_name.addItems(list(scanned.names))
            if scanned.rows:
                self.glyph_name.setCurrentIndex(scanned.names.index(scanned.rows[0].name))
        finally:
            self.glyph_name.blockSignals(blocked)
        self.publish(scanned)

    def publish(self, scanned: Snapshot) -> None:
        """Display a full measured row and preserve missing-versus-zero values."""
        self.snapshot = scanned
        row = scanned.rows[0] if scanned.rows else None
        for field, value in ((self.actual_advance, row.advance if row else None),
                             (self.actual_lsb, row.lsb if row else None)):
            field.setText("—" if value is None else f"{value:g}")
        self.preview_button.setEnabled(row is not None and row.advance is not None)
        if row is not None and row.advance is not None:
            self.advance_box.setValue(row.advance)
        self.result_label.setText("")
        self.status.setText(f"{scanned.master} · {len(scanned.names)} glyphs. No font edits.")

    def choose(self) -> None:
        """Read the chosen existing glyph only while the previous source is valid."""
        scanned = self.require_snapshot()
        ensure_current(api, scanned)
        self.publish(capture(api, "form", str(self.glyph_name.currentText)))

    def preview(self) -> None:
        """Refuse changed source and compare only plain width values."""
        scanned = self.require_snapshot()
        ensure_current(api, scanned)
        if not scanned.rows:
            raise ValueError("This font has no glyphs to preview.")
        self.result_label.setText(preview(scanned.rows[0], float(self.advance_box.value)))
