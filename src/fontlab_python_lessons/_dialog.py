# this_file: src/fontlab_python_lessons/_dialog.py
# SPDX-License-Identifier: Apache-2.0
"""Compose lessons on App's existing owned NamesDialog lifecycle.

Build Close/status before reading font data or loading a form. All failure
paths clear borrowed snapshots and actions while leaving the dialog closable.
"""
from collections.abc import Callable
from typing import Any

from fly import qt
from fly.ap import scripting as api

from .domain import Snapshot

BaseDialog = api.names_dialog_type()


class LessonDialog(BaseDialog):
    """Use App's signal ownership, registry and modeless dialog destruction."""

    def __init__(self, parent: Any, title: str, key: str) -> None:
        BaseDialog.__init__(self, parent, title, "examples-" + key)
        self.snapshot: Snapshot | None = None
        self.model: Any = None
        self.content = qt.QtGui.QVBoxLayout()
        self.root.addLayout(self.content, 1)
        self.status = qt.QtGui.QLabel("")
        self.status.setWordWrap(True)
        footer = qt.QtGui.QHBoxLayout()
        self.refresh_button = qt.QtGui.QPushButton("Refresh")
        self.close_button = qt.QtGui.QPushButton("Close")
        self.refresh_button.setAutoDefault(False)
        self.close_button.setAutoDefault(False)
        footer.addWidget(self.status, 1)
        footer.addWidget(self.refresh_button)
        footer.addWidget(self.close_button)
        self.root.addLayout(footer)
        self._connect(self.refresh_button.clicked, lambda *args: self.refresh())
        self._connect(self.close_button.clicked, lambda *args: self.close())
        self.setMinimumSize(580, 360)

    def start(self, build: Callable[[], None]) -> None:
        """Contain build/read faults after Close and status already exist."""
        try:
            build()
            self.refresh()
        except Exception as error:  # noqa: BLE001 - contain native UI build/read faults
            self.invalidate()
            self.status.setText(str(error))

    def invalidate(self) -> None:
        """Clear data, disable actions and detach the old model before deletion."""
        self.snapshot = None
        view = getattr(self, "view", None)
        if view is not None:
            view.setModel(None)
        if self.model is not None:
            self.model.deleteLater()
            self.model = None
        self.visible_names = ()
        for name in ("select_button", "filter_button", "preview_button"):
            control = getattr(self, name, None)
            if control is not None:
                control.setEnabled(False)
        for name in ("result_label", "actual_advance", "actual_lsb"):
            control = getattr(self, name, None)
            if control is not None:
                control.setText("")

    def require_snapshot(self) -> Snapshot:
        """Fail before any action when a source read has failed or been cleared."""
        if self.snapshot is None:
            raise ValueError("No current results. Click Refresh.")
        return self.snapshot

    def set_model(self, model: Any) -> None:
        """Replace a parent-owned model and release its obsolete Python reference."""
        previous = self.model
        self.model = model
        self.view.setModel(model)
        if previous is not None:
            previous.deleteLater()

    def closeEvent(self, event: Any) -> None:
        """Discard borrowed data; App disconnects every slot before deletion."""
        self.snapshot = None
        BaseDialog.closeEvent(self, event)

    def refresh(self) -> None:
        """Subclasses replace their complete snapshot and visible data."""
        raise NotImplementedError
