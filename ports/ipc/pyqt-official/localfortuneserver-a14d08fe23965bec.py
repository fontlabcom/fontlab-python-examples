# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/a14d08fe23965bec.md
# this_file: ports/ipc/pyqt-official/localfortuneserver-a14d08fe23965bec.py

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    item = getattr(obj, name)
    return item() if callable(item) else item


@contextmanager
def owned(qt, title):
    state = {"closing": False}

    class Window(qt.QtGui.QWidget):
        def closeEvent(self, event):
            if not state["closing"]:
                handle.close()
            event.accept()

    window = Window()
    handle = ExampleHandle(window, dict)
    handle.cleanup.append(lambda: state.update(closing=True))
    try:
        window.setWindowTitle(title)
        window.setAttribute(qt.QtCore.Qt.WA_QuitOnClose, False)
        window.resize(760, 540)
        layout = qt.QtGui.QVBoxLayout(window)
        handle.controls["layout"] = layout
        yield handle, layout
    except BaseException:
        handle.close()
        raise


def wire(handle, obj, signature, callback):
    def receive(*args):
        if not handle.owner.closed:
            callback(*args)

    handle.connect_old(obj, signature, receive)
    return receive


def button(qt, handle, layout, name, callback):
    item = qt.QtGui.QPushButton(name, handle.widget)
    layout.addWidget(item)
    handle.controls[name] = item
    wire(handle, item, "clicked()", lambda *args: callback())
    return item


import struct

FORTUNES = (
    "A quiet river remembers every bend.",
    "Small steps still cross a field.",
    "Leave a margin for surprise.",
    "A clear window welcomes the morning.",
    "Good questions travel further.",
    "A spare pencil is a useful friend.",
    "The next curve may open a view.",
)


def packet(text):
    payload = text.encode("utf-16-be")
    body = struct.pack(">I", len(payload)) + payload
    if len(body) > 65535:
        raise ValueError("Fortune is too large")
    return struct.pack(">H", len(body)) + body


def decode(buffer):
    if len(buffer) < 2:
        return None
    length = struct.unpack(">H", buffer[:2])[0]
    if length < 4 or length > 16384:
        raise ValueError("Invalid local fortune frame size")
    if len(buffer) < length + 2:
        return None
    if len(buffer) != length + 2:
        raise ValueError("Unexpected trailing local fortune data")
    body = buffer[2:]
    count = struct.unpack(">I", body[:4])[0]
    if count != len(body) - 4 or count % 2:
        raise ValueError("Invalid local fortune Unicode length")
    return body[4:].decode("utf-16-be")


def build(qt):
    core, gui, network = qt.QtCore, qt.QtGui, qt.QtNetwork
    with owned(qt, "Local fortune server") as (handle, layout):
        # AF_UNIX endpoints need a short pathname, independent of macOS TMPDIR.
        directory = TemporaryDirectory(prefix="flc-", dir="/tmp")
        handle.after_close.append(directory.cleanup)
        endpoint = str(Path(directory.name) / "peer")
        server = network.QLocalServer(handle.widget)
        client = network.QLocalSocket(handle.widget)
        status = gui.QLabel("Ready", handle.widget)
        name = gui.QLineEdit(endpoint, handle.widget)
        layout.addWidget(name)
        layout.addWidget(status)
        state = {
            "buffer": b"",
            "message": "",
            "retries": 0,
            "serial": 0,
            "pending": False,
            "accepted": [],
            "listening": False,
        }
        deadline = core.QTimer(handle.widget)
        deadline.setSingleShot(True)
        retry = core.QTimer(handle.widget)
        retry.setSingleShot(True)
        handle.cleanup.extend([deadline.stop, retry.stop])

        def fail(message):
            state["pending"] = False
            deadline.stop()
            retry.stop()
            client.abort()
            status.setText(message)

        def request(reset=True):
            if str(value(name, "text")) != endpoint:
                fail("Only this example's local endpoint is allowed")
                return
            deadline.stop()
            retry.stop()
            client.abort()
            state["buffer"] = b""
            state["pending"] = True
            if reset:
                state["retries"] = 0
            deadline.start(1500)
            client.connectToServer(endpoint)

        def accept(*args):
            while server.hasPendingConnections():
                socket = server.nextPendingConnection()
                state["accepted"].append(socket)
                text = FORTUNES[state["serial"] % len(FORTUNES)]
                state["serial"] += 1
                socket.write(core.QByteArray(packet(text)))
                socket.disconnectFromServer()
                while len(state["accepted"]) > 16:
                    expired = state["accepted"].pop(0)
                    expired.abort()
                    expired.deleteLater()

        def receive(*args):
            if not state["pending"]:
                return
            native = client.readAll()
            data = native.data() if hasattr(native, "data") else native
            state["buffer"] += bytes(data)
            if len(state["buffer"]) > 16386:
                fail("Local fortune frame exceeded the limit")
                return
            try:
                text = decode(state["buffer"])
            except (ValueError, UnicodeError) as error:
                fail(str(error))
                return
            if text is None:
                return
            deadline.stop()
            client.abort()
            state["pending"] = False
            if text == state["message"] and state["retries"] < 3:
                state["retries"] += 1
                retry.start(20)
                return
            state["message"] = text
            status.setText(text)

        def shutdown():
            deadline.stop()
            retry.stop()
            client.abort()
            for socket in state["accepted"]:
                socket.abort()
            server.close()
            if state["listening"]:
                network.QLocalServer.removeServer(endpoint)
                state["listening"] = False

        def release():
            for socket in state["accepted"]:
                socket.deleteLater()
            state["accepted"].clear()

        handle.cleanup.append(shutdown)
        handle.release.append(release)
        wire(handle, server, "newConnection()", accept)
        wire(handle, client, "readyRead()", receive)
        wire(
            handle,
            client,
            "error(QLocalSocket::LocalSocketError)",
            lambda *args: (
                fail(str(value(client, "errorString"))) if state["pending"] else None
            ),
        )
        wire(
            handle,
            deadline,
            "timeout()",
            lambda *args: (
                fail("Local fortune request timed out") if state["pending"] else None
            ),
        )
        wire(handle, retry, "timeout()", lambda *args: request(False))
        if not server.listen(endpoint):
            raise RuntimeError(
                "Cannot listen at the owned local endpoint: "
                + str(value(server, "errorString"))
            )
        state["listening"] = True
        button(qt, handle, layout, "Test owned client", request)
        button(qt, handle, layout, "Quit", handle.close)
        handle.controls.update(
            server=server,
            client=client,
            server_name=name,
            status=status,
            request=request,
            receive=receive,
            deadline=deadline,
            retry=retry,
            endpoint=endpoint,
        )
        handle.inspect_ui = lambda: {
            "endpoint": endpoint,
            "message": state["message"],
            "pending": state["pending"],
            "retries": state["retries"],
        }
        return handle
