# this_file: fontlab_python_examples/chat.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples numbered example 11.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json.
"""Chat variants with Python-only workers and GUI-owned delivery timers."""

from queue import Empty, Queue
from threading import Event, Thread
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .handle import ExampleHandle

CHAT_URL = "https://build-system.fman.io/chat"
HTTP_TIMEOUT = 2


def request_message(fields: dict | None = None) -> str:
    """Bound network waits; no Qt objects cross this I/O boundary."""
    data = None if fields is None else urlencode(fields).encode("utf-8")
    with urlopen(Request(CHAT_URL, data=data), timeout=HTTP_TIMEOUT) as response:
        return response.read(65536).decode("utf-8")


def build_chat(qt: Any, variant: str) -> ExampleHandle:
    gui = qt.QtGui
    stop = Event()
    incoming: Queue = Queue()
    outgoing: Queue = Queue()
    state = {"name": "", "error": "", "received_count": 0, "sent_count": 0}
    worker = None

    def shutdown(*_args: Any) -> None:
        stop.set()
        if worker is not None:
            worker.join()

    class Window(gui.QWidget):
        def closeEvent(self, event: Any) -> None:
            if not stop.is_set():
                timer.stop()
                shutdown()
            event.accept()

    window = Window()
    text_area = gui.QPlainTextEdit(window)
    text_area.setFocusPolicy(qt.QtCore.Qt.NoFocus)
    message = gui.QLineEdit(window)
    # input() would block an embedded GUI; collect the same name in the window.
    name = gui.QLineEdit(window)
    name.setPlaceholderText("Please enter your name: ")
    layout = gui.QVBoxLayout(window)
    for widget in (name, text_area, message):
        layout.addWidget(widget)
    timer = qt.QtCore.QTimer(window)
    handle = ExampleHandle(
        window,
        lambda: {
            **state,
            "name": str(name.text),
            "text": str(text_area.toPlainText()),
            "message": str(message.text),
            "variant": variant,
            "thread_alive": bool(worker and worker.is_alive()),
        },
    )

    def fetch() -> None:
        try:
            response = request_message()
            if response:
                incoming.put(("message", response))
        except (OSError, URLError, UnicodeError) as error:
            incoming.put(("error", str(error)))

    def run() -> None:
        while not stop.is_set():
            try:
                fields = outgoing.get_nowait()
            except Empty:
                fields = None
            if fields is not None:
                try:
                    request_message(fields)
                    incoming.put(("sent", ""))
                except (OSError, URLError, UnicodeError) as error:
                    incoming.put(("error", str(error)))
            if not stop.is_set():
                fetch()
            stop.wait(0.5)

    def display() -> None:
        if stop.is_set():
            return
        if variant == "single_threaded":
            fetch()
        while True:
            try:
                kind, value = incoming.get_nowait()
            except Empty:
                return
            if kind == "message":
                text_area.appendPlainText(value)
                state["received_count"] += 1
            elif kind == "sent":
                state["sent_count"] += 1
            else:
                state["error"] = value
                window.setWindowTitle("Chat: " + value)

    def send() -> None:
        fields = {"name": str(name.text), "message": str(message.text)}
        if variant == "single_threaded":
            try:
                request_message(fields)
                state["sent_count"] += 1
            except (OSError, URLError, UnicodeError) as error:
                state["error"] = str(error)
                return
        else:
            outgoing.put(fields)
        message.clear()

    def cleanup() -> None:
        if not handle.owner.closed:
            timer.stop()
        shutdown()

    handle.cleanup.append(cleanup)
    handle.callbacks.extend((display, send, shutdown))
    handle.connect(window.destroyed, shutdown)
    handle.connect(message.returnPressed, send)
    handle.connect(timer.timeout, display)
    timer.start(50 if variant == "with_threadutil" else 1000)
    if variant != "single_threaded":
        worker = Thread(target=run, name="fontlab-example-chat", daemon=True)
        worker.start()

    def release_widgets() -> None:
        nonlocal window, text_area, message, name, timer, worker
        window = text_area = message = name = timer = worker = None

    handle.release.append(release_widgets)
    return handle
