# this_file: ports/corelib/eyllanesc/main-cb1871959e42607b.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/corelib/ipc/localfortuneserver/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-


# Reuses the credited existing official port; its notices above remain applicable.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.official import Demo, LocalFortune

FORTUNES = (
    "You've been leading a dog's life. Stay off the furniture.",
    "You've got to think about tomorrow.",
    "You will be surprised by a loud noise.",
    "You will feel hungry again in another hour.",
    "You might have mail.",
    "You cannot kill time without injuring eternity.",
    "Computers are not intelligent. They only think they are.",
)


def build(qt: Any) -> ExampleHandle:
    demo = Demo(qt, __file__, "cb1871959e42607b")
    gui, core = qt.QtGui, qt.QtCore
    try:
        window = gui.QDialog()
        demo.begin(window)
        window.setWindowTitle("Fortune Server")
        layout = gui.QVBoxLayout(window)
        service = LocalFortune(demo, FORTUNES, frame_bytes=4)
        endpoint = demo.remember(
            "hostLineEdit", gui.QLineEdit(service.endpoint, window)
        )
        endpoint.setReadOnly(True)
        layout.addWidget(gui.QLabel("&Server name:", window))
        layout.addWidget(endpoint)
        status = demo.remember(
            "statusLabel",
            gui.QLabel(
                "The server is running.\nUse the owned peer to request a fortune.",
                window,
            ),
        )
        status.setWordWrap(True)
        layout.addWidget(status)
        get = demo.remember(
            "getFortuneButton", gui.QPushButton("Test owned client", window)
        )
        quit_button = demo.remember("quitButton", gui.QPushButton("Quit", window))
        layout.addWidget(get)
        layout.addWidget(quit_button)
        socket = demo.remember("socket", qt.QtNetwork.QLocalSocket(window))
        demo.handle.cleanup.insert(1, socket.abort)
        timer = demo.remember("requestTimer", core.QTimer(window))
        timer.setSingleShot(True)
        demo.handle.cleanup.append(timer.stop)
        state = {"fortune": "", "received": 0, "pending": False}
        incoming = bytearray()

        def failed(message: str) -> None:
            demo.error = message
            state["pending"] = False
            get.setEnabled(True)
            timer.stop()
            socket.abort()

        def request() -> None:
            if state["pending"]:
                return
            demo.error = ""
            incoming.clear()
            state["pending"] = True
            get.setEnabled(False)
            socket.abort()
            socket.connectToServer(service.endpoint)
            timer.start(2000)

        def ready() -> None:
            if not state["pending"]:
                return
            incoming.extend(socket.readAll().data())
            if len(incoming) < 4:
                return
            size = int.from_bytes(incoming[:4], "big")
            if size < 4:
                failed("Invalid local fortune frame size")
                return
            if len(incoming) < size + 4:
                return
            payload = incoming[4 : size + 4]
            length = int.from_bytes(payload[:4], "big")
            if length != len(payload) - 4 or length % 2:
                failed("Invalid local fortune QString length")
                return
            try:
                fortune = payload[4:].decode("utf-16-be")
            except UnicodeError as error:
                failed(str(error))
                return
            if fortune == state["fortune"]:
                state["pending"] = False
                socket.abort()
                # Original duplicate retry remains asynchronous and cancellable.
                timer.stop()
                retry.start(0)
                return
            state.update(fortune=fortune, pending=False, received=state["received"] + 1)
            status.setText(fortune)
            get.setEnabled(True)
            timer.stop()

        def socket_error(error: Any) -> None:
            if error != qt.QtNetwork.QLocalSocket.PeerClosedError and state["pending"]:
                failed(str(socket.errorString()))

        retry = demo.remember("retryTimer", core.QTimer(window))
        retry.setSingleShot(True)
        demo.handle.cleanup.append(retry.stop)
        demo.connect(retry, "timeout()", request)
        demo.connect(
            timer, "timeout()", lambda: failed("Owned local fortune request timed out")
        )
        demo.connect(socket, "readyRead()", ready)
        demo.connect(socket, "error(QLocalSocket::LocalSocketError)", socket_error)
        demo.connect(get, "clicked()", request)
        demo.connect(quit_button, "clicked()", window.close)
        demo.remember("requestNewFortune", request)
        return demo.finish(
            window, lambda: {**state, **service.snapshot(), "owned_endpoint": True}
        )
    except BaseException:
        demo.abort()
        raise


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("cb1871959e42607b")
