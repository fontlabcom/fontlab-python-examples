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
        self.cleanup: list[Callable] = []
        self.connections: list[tuple[Any, str | None, Callable]] = []
        self.release: list[Callable] = []
        self.model: Any = None
        self.controls: dict[str, Any] = {}

    def connect(self, signal: Any, slot: Callable) -> None:
        """Retain the exact signal/slot pair until explicit disconnection."""
        signal.connect(slot)
        self.connections.append((signal, None, slot))

    def connect_old(self, obj: Any, signature: str, slot: Callable) -> None:
        """Record PythonQt's string-signature connection without a bound disconnector."""
        obj.connect(signature, slot)
        self.connections.append((obj, signature, slot))

    def disconnect(self, signal: Any, slot: Callable) -> None:
        """Disconnect a tracked pair before dynamically unloading owned actions."""
        pair = (signal, None, slot)
        if pair not in self.connections:
            raise ValueError("Signal/slot pair is not tracked by this handle")
        if not self.owner.closed:
            signal.disconnect(slot)
        self.connections.remove(pair)

    def _disconnect(self) -> None:
        while self.connections:
            obj, signature, slot = self.connections[-1]
            if not self.owner.closed:
                if signature is None:
                    obj.disconnect(slot)
                else:
                    obj.disconnect(signature, slot)
            self.connections.pop()

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
        while self.cleanup:
            self.cleanup[0]()
            self.cleanup.pop(0)
        self._disconnect()
        self.callbacks.clear()
        self.inspect_ui = dict
        self.model = None
        self.controls.clear()
        while self.release:
            self.release.pop(0)()
        for alert in self.alerts:
            alert.close()
        self.alerts.clear()
        self.owner.close()
