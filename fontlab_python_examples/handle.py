# this_file: fontlab_python_examples/handle.py
"""Small ownership record, delegating native teardown to fontlabapp."""

from collections.abc import Callable
from typing import Any


class ExampleHandle:
    """Hold native UI/callbacks alive until named cleanup or native destruction."""

    def __init__(self, widget: Any, inspect_ui: Callable[[], dict]) -> None:
        from fontlabapp.widgets import OwnedWidget

        self.owner = OwnedWidget(widget, widget)
        self.inspect_ui = inspect_ui
        self.callbacks: list[Callable] = []
        self.alerts: list[Any] = []

    @property
    def widget(self) -> Any:
        return self.owner.widget

    def snapshot(self) -> dict:
        state = {"launched": True, "closed": self.owner.closed}
        if not self.owner.closed:
            state.update(visible=bool(self.widget.isVisible()))
            state.update(self.inspect_ui())
        return state

    def close(self) -> None:
        for alert in self.alerts:
            alert.close()
        self.alerts.clear()
        self.owner.close()
        self.callbacks.clear()
        self.inspect_ui = dict
