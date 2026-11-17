# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/ebf87d5f5390b0fd.md
# this_file: Scripts/Network/Loopback Transfer.py
"""Loopback Transfer with an owned local peer; no external server or font needed."""
import queue
import time
from fontlab_python_lessons import qt_demos as S
from fontlab_python_lessons.network_demos import (
    Session, TOTAL, CHUNK, attach_peer,
)

TITLE = "Fifty mebibyte loopback"
MAIN = False

def configure(s):
    gui, core, network = s.gui, s.core, s.qt.QtNetwork

    def serve(connection, stop, publish):
        count = 0
        deadline = time.monotonic() + 15
        while count < TOTAL and not stop.is_set() and time.monotonic() < deadline:
            try:
                data = connection.recv(min(65536, TOTAL - count))
            except TimeoutError:
                continue
            if not data:
                if count < TOTAL:
                    publish(("error", "Sender closed early"))
                return
            count += len(data)
            publish(("received", count))
        if count == TOTAL:
            publish(("complete", count))

    peer = attach_peer(s, serve)
    s.state.update(sent=0, received=0, active=False, error="")
    labels = []
    bars = []
    for text in ("Client", "Server"):
        label = gui.QLabel(text + ": idle", s.panel)
        s.layout.addWidget(label)
        labels.append(label)
        bar = s.keep(text, gui.QProgressBar(s.panel))
        bar.setRange(0, TOTAL)
        s.layout.addWidget(bar)
        bars.append(bar)
    client = network.QTcpSocket(s.window)
    client.setProxy(network.QNetworkProxy(network.QNetworkProxy.NoProxy))
    s.keep("socket", client)
    s.handle.cleanup.append(client.abort)
    offset = [0]
    pending = [b""]
    connected = [False]
    outstanding = [0]

    def failure(message):
        client.abort()
        connected[0] = False
        sender.stop()
        s.state.update(active=False, error=message)
        start_button.setEnabled(True)
        labels[0].setText(message)

    s.connect(client, "connected()", lambda: connected.__setitem__(0, True))
    s.connect(
        client,
        "error(QAbstractSocket::SocketError)",
        lambda *args: failure(str(client.errorString())) if s.state["active"] else None,
    )

    def write():
        if not s.state["active"]:
            return
        if (
            not connected[0]
            and client.state() != network.QAbstractSocket.ConnectedState
        ):
            return
        connected[0] = True
        for _ in range(4):
            if offset[0] >= TOTAL:
                sender.stop()
                break
            if outstanding[0] >= 262144:
                break
            data = pending[0] or CHUNK[: min(65536, TOTAL - offset[0])]
            count = int(client.write(core.QByteArray(data)))
            if count < 0:
                failure(str(client.errorString()))
                return
            if count == 0:
                break
            offset[0] += count
            outstanding[0] += count
            pending[0] = data[count:]
        s.state["sent"] = offset[0]
        bars[0].setValue(offset[0])
        labels[0].setText("Sent " + str(offset[0]))

    def acknowledged(count):
        outstanding[0] = max(0, outstanding[0] - int(count))

    s.connect(client, "bytesWritten(qint64)", acknowledged)

    def poll():
        for _ in range(32):
            try:
                kind, data = peer.events.get_nowait()
            except queue.Empty:
                break
            if kind in ("received", "complete"):
                s.state["received"] = data
                bars[1].setValue(data)
                labels[1].setText("Received " + str(data))
            if kind == "complete":
                s.state["active"] = False
                start_button.setEnabled(True)
                sender.stop()
                client.abort()
            elif kind == "error":
                failure(data)

    def start():
        if s.state["active"]:
            return False
        client.abort()
        offset[0] = 0
        pending[0] = b""
        connected[0] = False
        outstanding[0] = 0
        while not peer.events.empty():
            peer.events.get_nowait()
        s.state.update(sent=0, received=0, active=True, error="")
        start_button.setEnabled(False)
        client.connectToHost(peer.host, peer.port)
        sender.start(1)
        return True

    sender = s.timer("send", write, 1, start=False)
    s.timer("progress", poll, 30)
    start_button = s.button("Start", start)
    s.button("Quit", s.handle.close)
    s.keep("start", start)
    s.keep("write", write)
    s.keep("poll", poll)

def build(qt):
    with Session(qt, TITLE, MAIN) as session:
        configure(session)
        return session.finish()


def main():
    return S.launch(build, 'restored_loopback-ebf87d5f5390b0fd', 'Loopback Transfer')


if __name__ == "__main__":
    main()
