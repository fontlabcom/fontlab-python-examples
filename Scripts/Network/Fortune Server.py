# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/aad57160cfd51894.md
# this_file: Scripts/Network/Fortune Server.py
"""Fortune Server with an owned local peer; no external server or font needed."""
import queue
import socket
import threading
import time
from fontlab_python_lessons import qt_demos as S
from fontlab_python_lessons.qt_demos import value
from fontlab_python_lessons.network_demos import (
    Session, FORTUNES, fortune_frame, take_frame, attach_peer,
)

TITLE = "Loopback fortunes"
MAIN = False
MODE = "server"

def configure(s):
    import random

    gui, core, network = s.gui, s.core, s.qt.QtNetwork

    def serve(connection, stop, publish):
        packet = fortune_frame(random.choice(FORTUNES))
        # Deliberately fragment both framing and text.
        for index in range(0, len(packet), 3):
            if stop.is_set():
                return
            connection.sendall(packet[index : index + 3])
        publish(("served", len(packet)))

    peer = attach_peer(s, serve)
    status = s.keep(
        "status",
        gui.QLabel("Loopback peer at " + peer.host + ":" + str(peer.port), s.panel),
    )
    status.setTextFormat(core.Qt.PlainText)
    s.layout.addWidget(status)
    s.state.update(fortune="", error="", requests=0, busy=False)
    buffer = bytearray()
    client = [None]
    worker = [None]
    cancel_event = threading.Event()
    worker_results = queue.Queue(1)
    deadline = [0.0]

    def result(text):
        s.state.update(fortune=text, error="", busy=False)
        status.setText(text)
        if client[0] is not None:
            client[0].abort()
        if request_button[0]:
            request_button[0].setEnabled(True)

    def fail(message):
        s.state.update(error=message, busy=False)
        status.setText(message)
        if client[0] is not None:
            client[0].abort()
        if request_button[0]:
            request_button[0].setEnabled(True)

    def receive(data):
        buffer.extend(data)
        try:
            text = take_frame(buffer)
        except (ValueError, UnicodeError) as error:
            fail(str(error))
            return
        if text is not None:
            result(text)

    def cancel():
        cancel_event.set()
        if client[0] is not None:
            client[0].abort()
        if worker[0] is not None:
            worker[0].join(1)
            if worker[0].is_alive():
                raise RuntimeError("Fortune reader has not stopped")
            worker[0] = None
        s.state["busy"] = False

    def blocking_read(host, port, stop, output):
        connection = None
        try:
            connection = socket.create_connection((host, port), timeout=0.2)
            connection.settimeout(0.1)
            received = bytearray()
            end = time.monotonic() + 3
            while not stop.is_set() and time.monotonic() < end:
                try:
                    data = connection.recv(4096)
                except TimeoutError:
                    continue
                if not data:
                    raise ValueError("Peer ended before a complete fortune")
                received.extend(data)
                text = take_frame(received)
                if text is not None:
                    output.put(("fortune", text))
                    return
            if not stop.is_set():
                output.put(("error", "The fortune request timed out"))
        except (OSError, ValueError, UnicodeError) as error:
            if not stop.is_set():
                output.put(("error", str(error)))
        finally:
            if connection is not None:
                connection.close()

    def request(host=None, port=None):
        if s.state["busy"]:
            return False
        host = host if host is not None else str(value(host_control, "text"))
        port = port if port is not None else str(value(port_control, "text"))
        if host != peer.host or str(port) != str(peer.port):
            fail("Use the displayed owned numeric endpoint.")
            return False
        cancel()
        cancel_event.clear()
        buffer.clear()
        while not worker_results.empty():
            worker_results.get_nowait()
        s.state.update(busy=True, requests=s.state["requests"] + 1)
        deadline[0] = time.monotonic() + 3
        if request_button[0]:
            request_button[0].setEnabled(False)
        if MODE == "blocking":
            worker[0] = threading.Thread(
                target=blocking_read,
                args=(peer.host, peer.port, cancel_event, worker_results),
                name="owned-fortune-reader",
                daemon=True,
            )
            worker[0].start()
        else:
            if client[0] is None:
                native = network.QTcpSocket(s.window)
                native.setProxy(network.QNetworkProxy(network.QNetworkProxy.NoProxy))
                client[0] = s.keep("socket", native)
                s.connect(
                    native, "readyRead()", lambda: receive(native.readAll().data())
                )
                s.connect(
                    native,
                    "error(QAbstractSocket::SocketError)",
                    lambda *args: (
                        fail(str(native.errorString())) if s.state["busy"] else None
                    ),
                )
                s.handle.cleanup.append(native.abort)
            client[0].connectToHost(peer.host, peer.port)
        return True

    def poll():
        for _ in range(16):
            try:
                kind, data = worker_results.get_nowait()
            except queue.Empty:
                break
            if kind == "fortune":
                result(data)
            else:
                fail(data)
        if s.state["busy"] and time.monotonic() > deadline[0]:
            cancel()
            fail("The fortune request timed out")

    request_button = [None]
    host_control = s.keep("host", gui.QLineEdit(peer.host, s.panel))
    port_control = s.keep("port", gui.QLineEdit(str(peer.port), s.panel))
    if MODE in ("client", "blocking"):
        s.layout.addWidget(host_control)
        s.layout.addWidget(port_control)
        request_button[0] = s.button("Get Fortune", request)

        def valid(*args):
            request_button[0].setEnabled(
                not s.state["busy"]
                and str(value(host_control, "text")) == peer.host
                and str(value(port_control, "text")) == str(peer.port)
            )

        s.connect(host_control, "textChanged(QString)", valid)
        s.connect(port_control, "textChanged(QString)", valid)
    else:
        host_control.hide()
        port_control.hide()
    s.button("Quit", s.handle.close)
    s.timer("delivery", poll, 30)
    # Cancel readers before stopping the service or deleting their native peers.
    s.handle.cleanup.insert(1, cancel)
    s.keep("request", request)
    s.keep("receive", receive)
    s.keep("poll", poll)
    s.keep("cancel", cancel)

def build(qt):
    with Session(qt, TITLE, MAIN) as session:
        configure(session)
        return session.finish()


def main():
    return S.launch(build, 'restored_fortuneserver-aad57160cfd51894', 'Fortune Server')


if __name__ == "__main__":
    main()
