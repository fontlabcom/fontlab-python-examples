# this_file: ports/widgets/pyqt-examples/main-79cc15680bc2cebb.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann's pyqt/examples, src/04 PyQt Signals and Slots/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for exact provenance.
"""Original Click-to-alert behavior with asynchronous, example-window modality."""

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    button = qt.QtGui.QPushButton("Click")
    handle = ExampleHandle(button, lambda: _snapshot(handle))

    def on_button_clicked() -> None:
        _alert(qt, handle)

    handle.callbacks.append(on_button_clicked)
    try:
        button.clicked.connect(on_button_clicked)
    except BaseException:
        handle.close()
        raise
    return handle


def _snapshot(handle: ExampleHandle) -> dict:
    return {
        "text": str(handle.widget.text),
        "alert_texts": [
            str(alert.widget.text)
            for alert in handle.alerts
            if not alert.closed and alert.widget.isVisible()
        ],
    }


def _alert(qt: Any, handle: ExampleHandle) -> None:
    from fontlabapp.widgets import OwnedWidget

    for previous in handle.alerts:
        previous.close()
    handle.alerts.clear()
    alert = qt.QtGui.QMessageBox(handle.widget)
    owner = OwnedWidget(alert, alert)
    handle.alerts.append(owner)
    try:
        alert.setText("You clicked the button!")
        alert.setWindowModality(qt.QtCore.Qt.WindowModal)
        alert.open()
    except BaseException:
        owner.close()
        raise


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("79cc15680bc2cebb")
