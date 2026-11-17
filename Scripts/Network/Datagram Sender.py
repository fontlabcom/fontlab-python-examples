# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/90721289b8108c4f.md
# this_file: Scripts/Network/Datagram Sender.py
"""Datagram Sender with an owned local peer; no external server or font needed."""
import socket
from fontlab_python_lessons import qt_demos as S
from fontlab_python_lessons.network_demos import (
    Session,
)

TITLE = "Local datagrams"
MAIN = False
MODE = "sender"

def configure(s):
    gui, core = s.gui, s.core
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.bind(("127.0.0.1", 0))
    receiver.setblocking(False)
    s.handle.cleanup.append(receiver.close)
    host, port = receiver.getsockname()
    sender = s.qt.QtNetwork.QUdpSocket(s.window)
    sender.setProxy(s.qt.QtNetwork.QNetworkProxy(s.qt.QtNetwork.QNetworkProxy.NoProxy))
    s.handle.cleanup.append(sender.close)
    s.keep("sender", sender)
    s.keep("receiver", receiver)
    status = s.keep("status", gui.QLabel("Waiting for local datagrams", s.panel))
    s.layout.addWidget(status)
    messages = []
    s.state.update(endpoint=[host, port], sent=0, received=0, messages=messages)

    def sample_send():
        s.state["sent"] += 1
        text = "Local note " + str(s.state["sent"]) + ": a small signal arrives."
        data = core.QByteArray(text.encode("utf-8"))
        address = s.qt.QtNetwork.QHostAddress(s.qt.QtNetwork.QHostAddress.LocalHost)
        if sender.writeDatagram(data, address, port) < 0:
            s.state["error"] = str(sender.errorString())
        if MODE == "sender":
            status.setText("Sent " + str(s.state["sent"]))

    def poll():
        for _ in range(16):
            try:
                data, _peer = receiver.recvfrom(65536)
            except BlockingIOError:
                break
            text = data.decode("utf-8", errors="replace")
            messages.append(text)
            del messages[:-100]
            s.state["received"] += 1
            if MODE == "receiver":
                status.setText(text)

    interval = s.timer("send_timer", sample_send, 1000, start=False)
    if MODE == "sender":

        def start():
            if interval.isActive():
                return
            interval.start(1000)
            start_button.setEnabled(False)

        start_button = s.button("Start", start)
        s.keep("start", start)
    s.timer("receive_timer", poll, 30)
    s.button("Quit", s.handle.close)
    s.keep("sample_send", sample_send)
    s.keep("poll", poll)

def build(qt):
    with Session(qt, TITLE, MAIN) as session:
        configure(session)
        return session.finish()


def main():
    return S.launch(build, 'restored_broadcastsender-90721289b8108c4f', 'Datagram Sender')


if __name__ == "__main__":
    main()
