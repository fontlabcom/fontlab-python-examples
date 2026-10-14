# this_file: ports/network/eyllanesc/main-ecc2e23449331df1.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/network/loopback/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-


# Reuses the credited existing official port; its notices above remain applicable.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.official import Demo


def build(qt: Any) -> ExampleHandle:
    demo = Demo(qt, __file__, "ecc2e23449331df1")
    from fontlab_python_examples.official import LocalServer

    gui, core, network = (qt.QtGui, qt.QtCore, qt.QtNetwork)

    class Dialog(gui.QDialog):
        TotalBytes = 50 * 1024 * 1024
        PayloadSize = 65536

    window = Dialog()
    demo.begin(window)
    try:
        state = {"bytes_written": 0, "bytes_received": 0, "bytes_to_write": 0}
        clientProgressBar = gui.QProgressBar(window)
        serverProgressBar = gui.QProgressBar(window)
        clientStatusLabel = gui.QLabel("Client ready", window)
        serverStatusLabel = gui.QLabel("Server ready", window)
        startButton = gui.QPushButton("&Start", window)
        quitButton = gui.QPushButton("&Quit", window)
        layout = gui.QVBoxLayout(window)
        for obj in [
            clientProgressBar,
            clientStatusLabel,
            serverProgressBar,
            serverStatusLabel,
            startButton,
            quitButton,
        ]:
            layout.addWidget(obj)

        def receive(connection, stop, publish):
            total = 0
            while not stop.is_set():
                try:
                    data = connection.recv(65536)
                except TimeoutError:
                    continue
                if not data:
                    break
                total += len(data)
                publish(("received", total))

        def delivered(value):
            if value[0] == "request_error":
                demo.error = value[1]
                return
            state["bytes_received"] = value[1]
            serverProgressBar.setValue(value[1])
            serverStatusLabel.setText(f"Received {value[1] // (1024 * 1024):d}MB")
            if value[1] >= window.TotalBytes:
                startButton.setEnabled(True)

        endpoint = LocalServer(demo, receive, delivered)
        client = network.QTcpSocket(window)
        client.setProxy(network.QNetworkProxy(network.QNetworkProxy.NoProxy))
        demo.handle.cleanup.append(client.abort)

        def sendChunk():
            if state["bytes_to_write"] <= 0:
                return
            count = min(state["bytes_to_write"], window.PayloadSize)
            result = client.write(core.QByteArray(b"@" * count))
            if result < 0:
                demo.error = client.errorString()
                client.abort()
                startButton.setEnabled(True)
                return
            state["bytes_to_write"] -= result

        def progress(count):
            state["bytes_written"] += count
            clientProgressBar.setValue(state["bytes_written"])
            clientStatusLabel.setText(
                "Sent {:d}MB".format(state["bytes_written"] // (1024 * 1024))
            )
            if state["bytes_to_write"]:
                sendChunk()
            elif state["bytes_written"] >= window.TotalBytes:
                client.disconnectFromHost()

        def start():
            client.abort()
            state.update(
                bytes_written=0, bytes_received=0, bytes_to_write=window.TotalBytes
            )
            for bar in [clientProgressBar, serverProgressBar]:
                bar.setMaximum(window.TotalBytes)
                bar.setValue(0)
            startButton.setEnabled(False)
            serverStatusLabel.setText("Listening")
            clientStatusLabel.setText("Connecting")
            client.connectToHost(
                endpoint.host,
                endpoint.port,
                core.QIODevice.ReadWrite,
                network.QAbstractSocket.IPv4Protocol,
            )

        def failed(code):
            if code == network.QAbstractSocket.RemoteHostClosedError:
                return
            demo.error = client.errorString()
            client.abort()
            startButton.setEnabled(True)

        demo.connect(startButton, "clicked()", start)
        demo.connect(quitButton, "clicked()", window.close)
        demo.connect(client, "connected()", sendChunk)
        demo.connect(client, "bytesWritten(qint64)", progress)
        demo.connect(client, "error(QAbstractSocket::SocketError)", failed)
        window.setWindowTitle("Loopback")
        for key, obj in [
            ("startButton", startButton),
            ("quitButton", quitButton),
            ("clientProgressBar", clientProgressBar),
            ("serverProgressBar", serverProgressBar),
            ("clientStatusLabel", clientStatusLabel),
            ("serverStatusLabel", serverStatusLabel),
            ("tcpClient", client),
            ("serverTimer", endpoint.delivery.timer),
        ]:
            demo.remember(key, obj)
        return demo.finish(
            window,
            lambda: {
                **state,
                "endpoint": endpoint.snapshot(),
                "total_bytes": window.TotalBytes,
            },
        )
    except BaseException:
        demo.abort()
        raise


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("ecc2e23449331df1")
