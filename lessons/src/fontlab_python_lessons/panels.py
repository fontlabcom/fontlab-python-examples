# this_file: lessons/src/fontlab_python_lessons/panels.py
# SPDX-License-Identifier: Apache-2.0
"""Teach native list/table models using real current-font data and safe actions."""
from typing import Any

from fly import qt
from fly.ap import scripting as api

from ._dialog import LessonDialog
from .domain import capture, ensure_current, filtered
from .models import metrics_model


class GlyphNameFilter(LessonDialog):
    """Filter a font's actual names and select explicitly chosen result rows."""

    def __init__(self, parent: Any = None) -> None:
        LessonDialog.__init__(self, parent, "Glyph Name Filter", "glyph-name-filter")
        self.subtitle.setText("Filter names in font order. Select changes only Font window selection.")
        self.start(self.build)

    def build(self) -> None:
        """Create the native list view and explicit filter/select controls."""
        self.query = qt.QtGui.QLineEdit()
        self.query.setPlaceholderText("Glyph name prefix; empty shows all names")
        self.filter_button = qt.QtGui.QPushButton("Apply Prefix")
        self.select_button = qt.QtGui.QPushButton("Select Chosen Rows")
        self.view = qt.QtGui.QListView()
        self.view.setSelectionMode(qt.QtGui.QAbstractItemView.ExtendedSelection)
        self.view.setEditTriggers(qt.QtGui.QAbstractItemView.NoEditTriggers)
        for control in (self.query, self.filter_button, self.view, self.select_button):
            self.content.addWidget(control)
        self._connect(self.filter_button.clicked, lambda *args: self.apply_filter())
        self._connect(self.select_button.clicked, lambda *args: self.select())

    def refresh(self) -> None:
        """Adopt current font/master/membership only after a complete read."""
        self.invalidate()
        self.snapshot = capture(api, "names")
        self.filter_button.setEnabled(True)
        self.apply_filter()

    def apply_filter(self) -> None:
        """Reject stale membership before replacing the displayed result list."""
        scanned = self.require_snapshot()
        ensure_current(api, scanned)
        self.visible_names = filtered(scanned.names, str(self.query.text))
        self.set_model(qt.QtGui.QStringListModel(list(self.visible_names), self))
        self.select_button.setEnabled(bool(self.visible_names))
        self.status.setText(f"{len(self.visible_names)} of {len(scanned.names)} glyphs · {scanned.master}")

    def select(self) -> None:
        """Select chosen visible rows; refuse stale source before any selection edit."""
        scanned = self.require_snapshot()
        ensure_current(api, scanned)
        rows = {index.row() for index in self.view.selectedIndexes()}
        names = [name for row, name in enumerate(self.visible_names) if row in rows]
        if not names:
            raise ValueError("Choose one or more result rows first.")
        selected = api.select_glyphs(names, package_id=scanned.package_id)
        self.status.setText(f"Selected {len(selected)} glyphs. Font data unchanged.")


class GlyphMetricsModel(LessonDialog):
    """Display exact current-master metrics for the Font window selection."""

    def __init__(self, parent: Any = None) -> None:
        LessonDialog.__init__(self, parent, "Glyph Metrics Model", "glyph-metrics-model")
        self.subtitle.setText("Read-only table model. Refresh adopts the current selection and master. — means unavailable.")
        self.start(self.build)

    def build(self) -> None:
        """Create an actual Qt table view; all editing remains disabled."""
        self.view = qt.QtGui.QTableView()
        self.view.setEditTriggers(qt.QtGui.QAbstractItemView.NoEditTriggers)
        self.view.setAlternatingRowColors(True)
        self.content.addWidget(self.view)

    def refresh(self) -> None:
        """Publish measured rows atomically, including empty and zero-width glyphs."""
        self.invalidate()
        scanned = capture(api, "metrics")
        self.set_model(metrics_model(qt, scanned.rows, self))
        self.view.resizeColumnsToContents()
        self.snapshot = scanned
        self.status.setText(f"{len(scanned.rows)} selected glyphs · {scanned.master}. Refresh after edits.")
