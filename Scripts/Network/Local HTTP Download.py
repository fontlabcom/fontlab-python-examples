# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/409f3d46a9555f23.md
# this_file: Scripts/Network/Local HTTP Download.py
"""Local HTTP Download with an owned local peer; no external server or font needed."""
from fontlab_python_lessons import qt_demos as S
from fontlab_python_lessons.qt_demos import value
from fontlab_python_lessons.network_demos import (
    Session, http_peer, local_url, network_manager, request_for, retire_reply,
)

TITLE = "Owned sample download"
MAIN = False

def configure(s):
    peer = http_peer(s)
    manager = network_manager(s)
    base = "http://" + peer.host + ":" + str(peer.port)
    url_control = s.keep("url", s.gui.QLineEdit(base + "/sample", s.panel))
    s.layout.addWidget(url_control)
    status = s.keep("status", s.gui.QLabel("Ready", s.panel))
    s.layout.addWidget(status)
    s.state.update(active=False, bytes=0, error="", output=None)
    active = [None]
    output = [None]
    progress = [None]
    stream = [None]

    def cancel():
        reply = active[0]
        active[0] = None
        if reply is not None:
            reply.abort()
            retire_reply(s, reply)
        if stream[0] is not None:
            stream[0].close()
            stream[0] = None
        if output[0] is not None:
            output[0].unlink(missing_ok=True)
        if progress[0] is not None:
            progress[0].hide()
        s.state["active"] = False
        button.setEnabled(True)

    def fail(message):
        cancel()
        s.state["error"] = message
        status.setText(message)

    def download(text=None):
        if s.state["active"]:
            return False
        text = str(value(url_control, "text")) if text is None else str(text)
        try:
            parsed = local_url(text, peer)
            if parsed.path not in ("/sample", "/error", "/redirect") or parsed.query:
                raise ValueError("Unknown owned download")
        except (ValueError, TypeError) as error:
            fail(str(error))
            return False
        s.state.update(active=True, bytes=0, error="", output=None)
        button.setEnabled(False)
        output[0] = s.root() / "sample.part"
        try:
            stream[0] = output[0].open("wb")
        except OSError as error:
            fail(str(error))
            return False
        box = s.gui.QProgressDialog("Receiving local sample", "Cancel", 0, 0, s.window)
        box.setAutoClose(False)
        progress[0] = box
        s.connect(box, "canceled()", cancel)
        s.dialog(box)
        try:
            reply = manager.get(request_for(s, text))
        except (OSError, ValueError, RuntimeError) as error:
            fail(str(error))
            return False
        active[0] = reply

        def consume():
            if active[0] is not reply:
                return
            data = reply.readAll().data()
            try:
                stream[0].write(data)
            except OSError as error:
                fail(str(error))
                return
            s.state["bytes"] += len(data)

        def finish():
            if active[0] is not reply:
                return
            consume()
            if active[0] is not reply:
                return
            redirect = reply.attribute(
                s.qt.QtNetwork.QNetworkRequest.RedirectionTargetAttribute
            )
            if redirect or reply.error():
                return fail("Download rejected a redirect or HTTP failure")
            final = s.root() / "sample.txt"
            try:
                stream[0].close()
                stream[0] = None
                output[0].replace(final)
            except OSError as error:
                fail(str(error))
                return
            output[0] = None
            active[0] = None
            retire_reply(s, reply)
            box.hide()
            s.state.update(active=False, output=str(final))
            button.setEnabled(True)
            status.setText("Saved " + str(s.state["bytes"]) + " bytes")

        s.connect(reply, "readyRead()", consume)
        s.connect(reply, "finished()", finish)
        deadline.start(3000)
        return True

    button = s.button("Download", download)
    s.button("Quit", s.handle.close)
    deadline = s.timer(
        "deadline",
        lambda: fail("Download timed out") if s.state["active"] else None,
        3000,
        start=False,
        once=True,
    )
    s.handle.cleanup.insert(1, cancel)
    s.keep("download", download)
    s.keep("cancel", cancel)

def build(qt):
    with Session(qt, TITLE, MAIN) as session:
        configure(session)
        return session.finish()


def main():
    return S.launch(build, 'restored_http-409f3d46a9555f23', 'Local HTTP Download')


if __name__ == "__main__":
    main()
