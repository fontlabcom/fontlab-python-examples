# this_file: tests/test_task6c_network_threads.py
# SPDX-License-Identifier: Apache-2.0
"""Drive local networking and worker panels with deterministic owned transports."""
import queue
import struct
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from test_restored_ui import qt, load, ROOT
from _cov_support import Signal


class Transport:
    def __init__(self, *args):
        self.readyRead, self.error = Signal(), Signal()
        self.connected, self.bytesWritten, self.newConnection = Signal(), Signal(), Signal()
        self.incoming = b''
        self.written = []
        self.pending = []
        self.write_result = None
        self.aborted = False
        self.deleted = False
        self.listening = True

    def setProxy(self, proxy):
        pass

    def connectToHost(self, host, port):
        self.endpoint = host, port
        self.connected.emit()

    def connectToServer(self, endpoint):
        self.endpoint = endpoint

    def state(self):
        return 1

    def write(self, data):
        self.written.append(bytes(data))
        return len(data) if self.write_result is None else self.write_result

    def writeDatagram(self, data, address, port):
        return self.write(data)

    def readAll(self):
        data, self.incoming = self.incoming, b''
        return NS(data=lambda: data)

    def abort(self):
        self.aborted = True

    def close(self):
        self.abort()

    def disconnectFromServer(self):
        self.aborted = True

    def deleteLater(self):
        self.deleted = True

    def errorString(self):
        return 'owned transport error'

    def listen(self, endpoint):
        return self.listening

    def hasPendingConnections(self):
        return bool(self.pending)

    def nextPendingConnection(self):
        return self.pending.pop(0)

    @staticmethod
    def removeServer(endpoint):
        return True


@pytest.fixture
def netqt(qt):
    qt.QtNetwork = NS(
        QTcpSocket=Transport, QUdpSocket=Transport, QLocalServer=Transport,
        QLocalSocket=Transport, QAbstractSocket=NS(ConnectedState=1),
        QNetworkProxy=lambda *a: None,
        QHostAddress=lambda *a: None,
        QNetworkRequest=NS(RedirectionTargetAttribute=1),
    )
    class Proxy:
        NoProxy = 0
        def __init__(self, *args):
            pass
    class Address:
        LocalHost = 0
        def __init__(self, *args):
            pass
    qt.QtNetwork.QNetworkProxy = Proxy
    qt.QtNetwork.QHostAddress = Address
    return qt


def fake_peer(monkeypatch, module):
    def attach(session, serve):
        peer = NS(host='127.0.0.1', port=41001, events=queue.Queue(), serve=serve)
        session.keep('peer', peer)
        return peer
    monkeypatch.setattr(module, 'attach_peer', attach)


def launch_and_build(monkeypatch, module, qt):
    monkeypatch.setattr(module.S, 'launch', lambda builder, key, title: builder(qt))
    return module.main()


@pytest.mark.parametrize('title', ['Fortune Client', 'Fortune Server', 'Threaded Fortune Server', 'Blocking Fortune Client'])
def test_fortune_panels_fragment_errors_worker_and_endpoint(title, netqt, monkeypatch):
    m = load(ROOT / f'Scripts/Network/{title}.py')
    fake_peer(monkeypatch, m)
    h = launch_and_build(monkeypatch, m, netqt)
    c = h.controls
    try:
        assert not c['request']('example.invalid', 80)
        assert 'numeric endpoint' in c['status'].text()
        # The worker reader is exercised synchronously, with fragmented data and EOF.
        class Reader:
            def __init__(self, packets):
                self.packets = iter(packets)
                self.closed = False
            def settimeout(self, timeout):
                pass
            def recv(self, size):
                data = next(self.packets, b'')
                if isinstance(data, BaseException):
                    raise data
                return data
            def close(self):
                self.closed = True
        packet = m.fortune_frame('A quiet Unicode 曲線')
        reader = Reader([TimeoutError(), packet[:3], packet[3:]])
        monkeypatch.setattr(m.socket, 'create_connection', lambda *a, **k: reader)
        m.MODE = 'blocking'
        assert c['request']()
        assert not c['request']()
        deadline = time.monotonic() + 1
        while h.inspect_ui()['busy'] and time.monotonic() < deadline:
            c['poll']()
        assert h.inspect_ui()['fortune'] == 'A quiet Unicode 曲線'
        assert reader.closed
        c['cancel']()
        reader = Reader([b''])
        assert c['request']()
        deadline = time.monotonic() + 1
        while h.inspect_ui()['busy'] and time.monotonic() < deadline:
            c['poll']()
        assert 'complete fortune' in h.inspect_ui()['error']
        c['cancel']()
        m.MODE = 'client'
        assert c['request']()
        native = c['socket']
        native.incoming = packet[:3]
        native.readyRead.emit()
        assert h.inspect_ui()['busy']
        native.incoming = packet[3:]
        native.readyRead.emit()
        assert h.inspect_ui()['fortune'] == 'A quiet Unicode 曲線'
        native.error.emit()
        assert c['request']()
        c['receive'](b'\0\1x')
        assert 'Invalid fortune length' in c['status'].text()
        assert c['request']()
        native.error.emit()
        assert 'transport error' in c['status'].text()
        assert c['request']()
        now = m.time.monotonic()
        monkeypatch.setattr(m.time, 'monotonic', lambda: now + 10)
        c['poll']()
        assert 'timed out' in c['status'].text()
        writes, events = [], []
        peer = c['peer']
        peer.serve(NS(sendall=writes.append), threading.Event(), events.append)
        assert m.take_frame(bytearray(b''.join(writes))) in m.FORTUNES
        assert events[0][0] == 'served'
        stopped = threading.Event()
        stopped.set()
        peer.serve(NS(sendall=lambda data: pytest.fail('sent after cancel')), stopped, events.append)
        c['host'].setText('bad')
        c['host'].setText(peer.host)
        c['port'].setText('80')
        c['port'].setText(str(peer.port))
    finally:
        h.close()


class Datagram:
    def __init__(self, *args):
        self.packets = []
        self.closed = False
    def bind(self, endpoint):
        assert endpoint == ('127.0.0.1', 0)
    def setblocking(self, value):
        pass
    def settimeout(self, value):
        pass
    def getsockname(self):
        return '127.0.0.1', 41001
    def recvfrom(self, size):
        if not self.packets:
            raise BlockingIOError()
        return self.packets.pop(0), ('127.0.0.1', 41002)
    def close(self):
        self.closed = True


@pytest.mark.parametrize('title', ['Datagram Sender', 'Datagram Receiver'])
def test_datagram_controls_publish_decode_and_limit_history(title, netqt, monkeypatch):
    m = load(ROOT / f'Scripts/Network/{title}.py')
    monkeypatch.setattr(m.socket, 'socket', Datagram)
    h = launch_and_build(monkeypatch, m, netqt)
    try:
        c = h.controls
        c['sample_send']()
        assert b'Local note 1' in c['sender'].written[0]
        c['sender'].write_result = -1
        c['sample_send']()
        assert h.inspect_ui()['error'] == 'owned transport error'
        c['receiver'].packets.extend([b'hello', b'\xff'] + [b'again'] * 110)
        for _ in range(8):
            c['poll']()
        assert h.inspect_ui()['received'] == 112
        assert len(h.inspect_ui()['messages']) == 100
        if 'start' in c:
            c['Start'].click()
            c['start']()
            assert c['send_timer'].isActive()
            assert not c['Start'].isEnabled()
        else:
            assert c['status'].text() == 'again'
    finally:
        h.close()


class Reply:
    def __init__(self, data=b'hello', failure=False, redirect=False):
        self.readyRead, self.finished = Signal(), Signal()
        self.data, self.failure, self.redirect = data, failure, redirect
        self.aborted = self.deleted = False
    def readAll(self):
        data, self.data = self.data, b''
        return NS(data=lambda: data)
    def attribute(self, kind):
        return self.redirect
    def error(self):
        return self.failure
    def abort(self):
        self.aborted = True
    def deleteLater(self):
        self.deleted = True


def fake_http(monkeypatch, m):
    manager = NS(replies=[])
    def get(request):
        reply = Reply()
        manager.replies.append(reply)
        return reply
    manager.get = get
    monkeypatch.setattr(m, 'http_peer', lambda s: NS(host='127.0.0.1', port=41001))
    monkeypatch.setattr(m, 'network_manager', lambda s: manager)
    monkeypatch.setattr(m, 'request_for', lambda s, text: text)
    monkeypatch.setattr(m, 'retire_reply', lambda s, reply: reply.deleteLater())
    return manager


def test_http_download_success_cancel_reject_redirect_and_timeout(netqt, monkeypatch, tmp_path):
    m = load(ROOT / 'Scripts/Network/Local HTTP Download.py')
    manager = fake_http(monkeypatch, m)
    monkeypatch.setattr(m.Session, 'root', lambda s: tmp_path)
    h = launch_and_build(monkeypatch, m, netqt)
    try:
        c = h.controls
        assert not c['download']('http://example.invalid/sample')
        assert not c['download']('http://127.0.0.1:41001/missing')
        assert not c['download']('http://127.0.0.1:41001/sample?q=1')
        assert c['download']()
        assert not c['download']()
        reply = manager.replies[-1]
        reply.readyRead.emit()
        assert (tmp_path / 'sample.part').exists()
        reply.finished.emit()
        assert Path(h.inspect_ui()['output']).read_bytes() == b'hello'
        assert c['Download'].isEnabled()
        reply.readyRead.emit()
        reply.finished.emit()
        assert c['download']()
        reply = manager.replies[-1]
        reply.redirect = True
        reply.finished.emit()
        assert 'redirect' in c['status'].text()
        assert not (tmp_path / 'sample.part').exists()
        assert c['download']()
        reply = manager.replies[-1]
        c['cancel']()
        assert reply.aborted
        reply.readyRead.emit()
        reply.finished.emit()
        assert c['download']()
        c['deadline'].timeout.emit()
        assert 'timed out' in c['status'].text()
        c['deadline'].timeout.emit()
        def fail(request):
            raise OSError('request refused')
        monkeypatch.setattr(manager, 'get', fail)
        assert not c['download']()
        assert 'request refused' in c['status'].text()
    finally:
        h.close()


def test_map_tiles_navigation_night_magnifier_and_pixels(netqt, monkeypatch):
    from fontlab_python_lessons.network_demos import tile_png
    m = load(ROOT / 'Scripts/Network/Local Tile Map.py')
    manager = fake_http(monkeypatch, m)
    h = launch_and_build(monkeypatch, m, netqt)
    try:
        c = h.controls
        canvas = c['map']
        c['fetch']()
        count = len(manager.replies)
        c['fetch']()
        assert len(manager.replies) == count
        for reply in list(manager.replies):
            reply.data = tile_png(0, 0)
            reply.finished.emit()
            reply.finished.emit()
        assert h.inspect_ui()['cache'] == count
        picture = canvas.grab().toImage()
        assert not picture.isNull()
        c['Night'].click()
        assert h.inspect_ui()['night']
        assert canvas.grab().toImage() != picture
        c['hold'].timeout.emit()
        assert h.inspect_ui()['magnifier']
        assert not canvas.grab().isNull()
        core, gui = netqt.QtCore, netqt.QtGui
        canvas.mouseMoveEvent(NS(pos=lambda: core.QPoint(1, 1)))
        canvas.mousePressEvent(NS(pos=lambda: core.QPoint(10, 10)))
        canvas.mouseMoveEvent(NS(pos=lambda: core.QPoint(20, 25)))
        canvas.mouseReleaseEvent(NS())
        assert not h.inspect_ui()['magnifier']
        for key in (core.Qt.Key_Left, core.Qt.Key_Right, core.Qt.Key_Up, core.Qt.Key_Down, core.Qt.Key_A):
            canvas.keyPressEvent(gui.QKeyEvent(core.QEvent.KeyPress, key, core.Qt.NoModifier))
        c['city'](1)
        c['City'].setCurrentIndex(2)
        c['Information'].click()
        c['pan'](0, -100000)
        assert h.inspect_ui()['center'][1] == 0
        assert h.inspect_ui()['requests'] > count
    finally:
        h.close()


def test_loopback_partial_writes_acknowledgements_completion_and_failure(netqt, monkeypatch):
    m = load(ROOT / 'Scripts/Network/Loopback Transfer.py')
    fake_peer(monkeypatch, m)
    monkeypatch.setattr(m, 'TOTAL', 100)
    h = launch_and_build(monkeypatch, m, netqt)
    try:
        c = h.controls
        c['write']()
        assert c['start']()
        assert not c['start']()
        native = c['socket']
        native.write_result = 0
        c['write']()
        assert h.inspect_ui()['sent'] == 0
        native.write_result = 10
        c['write']()
        assert h.inspect_ui()['sent'] == 40
        native.bytesWritten.emit(40)
        native.write_result = None
        c['write']()
        assert h.inspect_ui()['sent'] == 100
        peer = c['peer']
        peer.events.put(('received', 50))
        peer.events.put(('complete', 100))
        c['poll']()
        assert not h.inspect_ui()['active']
        assert c['Server'].value() == 100
        assert c['start']()
        native.write_result = -1
        c['write']()
        assert 'transport error' in h.inspect_ui()['error']
        assert c['start']()
        native.error.emit()
        assert not h.inspect_ui()['active']
        assert c['start']()
        peer.events.put(('error', 'receiver stopped'))
        c['poll']()
        assert h.inspect_ui()['error'] == 'receiver stopped'
        events = []
        incoming = iter([TimeoutError(), b'x' * 40, b'x' * 60])
        def receive(size):
            data = next(incoming, b'')
            if isinstance(data, BaseException):
                raise data
            return data
        peer.serve(NS(recv=receive), threading.Event(), events.append)
        assert events[-1] == ('complete', 100)
        peer.serve(NS(recv=lambda n: b''), threading.Event(), events.append)
        assert events[-1] == ('error', 'Sender closed early')
    finally:
        h.close()


@pytest.mark.parametrize('title', ['Local Fortune Client', 'Local Fortune Server'])
def test_local_socket_fragment_retry_validation_timeout_and_cleanup(title, netqt, monkeypatch):
    m = load(ROOT / f'Scripts/IPC/{title}.py')
    h = launch_and_build(monkeypatch, m, netqt)
    c = h.controls
    try:
        c['server_name'].setText('outside')
        c['Get Fortune' if title.endswith('Client') else 'Test owned client'].click()
        assert 'Only this example' in c['status'].text()
        c['server_name'].setText(c['endpoint'])
        c['request']()
        assert h.inspect_ui()['pending']
        client, server = c['client'], c['server']
        accepted = [Transport() for _ in range(18)]
        server.pending.extend(accepted)
        server.newConnection.emit()
        assert accepted[0].deleted and len(accepted[0].written) == 1
        frame = m.packet('A quiet curve')
        client.incoming = frame[:3]
        client.readyRead.emit()
        assert h.inspect_ui()['pending']
        client.incoming = frame[3:]
        client.readyRead.emit()
        assert c['status'].text() == 'A quiet curve'
        client.readyRead.emit()
        c['request']()
        client.incoming = frame
        client.readyRead.emit()
        assert h.inspect_ui()['retries'] == 1
        c['retry'].timeout.emit()
        client.incoming = m.packet('Another quiet curve')
        client.readyRead.emit()
        assert c['status'].text() == 'Another quiet curve'
        c['request']()
        client.incoming = b'\0\1x'
        client.readyRead.emit()
        assert 'Invalid' in c['status'].text()
        c['request']()
        client.incoming = b'x' * 16387
        client.readyRead.emit()
        assert 'limit' in c['status'].text()
        c['request']()
        client.error.emit()
        assert 'transport error' in c['status'].text()
        client.error.emit()
        c['request']()
        c['deadline'].timeout.emit()
        c['deadline'].timeout.emit()
        assert 'timed out' in c['status'].text()
        assert m.value(NS(answer=4), 'answer') == 4
        # Reject malformed Unicode lengths before conversion.
        with pytest.raises(ValueError, match='Unicode length'):
            m.decode(b'\0\x06' + struct.pack('>I', 1) + b'aa')
    finally:
        h.close()
    assert all(item.aborted for item in accepted)


@pytest.mark.parametrize('title', ['Semaphore Transfer', 'Condition Variable Transfer'])
def test_transfer_panel_runs_ordered_data_and_stop_cancels_workers(title, qt, monkeypatch):
    m = load(ROOT / f'Scripts/Threads/{title}.py')
    monkeypatch.setattr(m, 'TOTAL', 512)
    h = launch_and_build(monkeypatch, m, qt)
    try:
        c = h.controls
        c['poll']()
        c['Start'].click()
        worker = c['transfer']()
        for thread in worker.threads:
            thread.join(1)
        c['timer'].timeout.emit()
        assert h.inspect_ui()['received'] == 512
        assert c['log'].toPlainText().endswith('ACGT' * 128)
        c['Stop'].click()
        assert not h.inspect_ui()['running']
        assert not worker.deliver('after stop')
        assert not worker.acquire(worker.free)
        c['start']()
        c['stop']()
        assert not h.inspect_ui()['running']
        # Both synchronization strategies implement the same ordered transfer.
        monkeypatch.setattr(m, 'USE_SEMAPHORES', not m.USE_SEMAPHORES)
        c['start']()
        for thread in c['transfer']().threads:
            thread.join(1)
        c['poll']()
        assert h.inspect_ui()['received'] == 512
        assert c['log'].toPlainText().endswith('ACGT' * 128)
    finally:
        h.close()


def test_mandelbrot_navigation_progress_render_and_cancel(qt, monkeypatch):
    m = load(ROOT / 'Scripts/Threads/Mandelbrot Explorer.py')
    h = launch_and_build(monkeypatch, m, qt)
    c = h.controls
    try:
        core, gui = qt.QtCore, qt.QtGui
        canvas = c['canvas']
        canvas.resize(32, 32)
        before = h.inspect_ui()
        for key in (core.Qt.Key_Plus, core.Qt.Key_Equal, core.Qt.Key_Minus,
                    core.Qt.Key_Left, core.Qt.Key_Right, core.Qt.Key_Up,
                    core.Qt.Key_Down, core.Qt.Key_A):
            canvas.keyPressEvent(gui.QKeyEvent(core.QEvent.KeyPress, key, core.Qt.NoModifier))
        for y in (-120, 120):
            canvas.wheelEvent(NS(angleDelta=lambda: core.QPoint(0, y), accept=lambda: None))
        canvas.mouseReleaseEvent(NS(pos=lambda: core.QPoint(1, 1)))
        canvas.mousePressEvent(NS(pos=lambda: core.QPoint(10, 10)))
        canvas.mouseReleaseEvent(NS(pos=lambda: core.QPoint(15, 20)))
        assert h.inspect_ui()['generation'] > before['generation']
        c['poll']()
        deadline = time.monotonic() + 1
        while h.inspect_ui()['pass'] == 0 and time.monotonic() < deadline:
            c['poll']()
        assert h.inspect_ui()['pass'] >= 1
        image = canvas.grab().toImage()
        assert not image.isNull()
        assert image.pixelColor(0, 0).alpha() == 255
        c['request']()
        c['poll']()
        # Repeated polling must safely discard an obsolete generation.
        for _ in range(20):
            c['poll']()
        assert m.scanline(2, 2, 1, (0, 0), 0, 24) == [0, 0]
    finally:
        h.close()


def test_schema_panel_validates_marks_errors_and_highlights(qt, monkeypatch):
    m = load(ROOT / 'Scripts/XML/Schema Validation.py')
    class Messages:
        def __init__(self, *args):
            pass
    class Schema:
        def setMessageHandler(self, handler):
            self.messages = handler
        def load(self, data, url):
            return b'bad-schema' not in bytes(data)
    class Validator:
        def __init__(self, schema):
            self.schema = schema
        def setMessageHandler(self, handler):
            self.messages = handler
        def validate(self, data, url):
            text = bytes(data).decode()
            valid = 'unexpected' not in text and '-2' not in text and 'none' not in text
            if not valid:
                self.messages.handleMessage(0, '<b>Invalid field</b>', None, NS(line=2, column=3))
            return valid
    qt.QtXmlPatterns = NS(QAbstractMessageHandler=Messages, QXmlSchema=Schema, QXmlSchemaValidator=Validator)
    h = launch_and_build(monkeypatch, m, qt)
    try:
        c = h.controls
        assert h.inspect_ui()['valid'] is True
        for index in range(3):
            c['family'].setCurrentIndex(index)
            c['variant'].setCurrentIndex(1)
            assert h.inspect_ui()['valid'] is False
            assert c['instance'].extraSelections()
            assert h.inspect_ui()['diagnostic'] == 'Invalid field'
            c['variant'].setCurrentIndex(0)
            assert h.inspect_ui()['valid']
        c['instance'].setPlainText('<broken>')
        c['Validate'].click()
        assert h.inspect_ui()['line'] == 1
        c['instance'].setPlainText('<!DOCTYPE a><a/>')
        c['validate']()
        assert 'DTD' in c['status'].text()
        c['schema'].setPlainText('<bad-schema/>')
        c['instance'].setPlainText('<root/>')
        c['validate']()
        assert not h.inspect_ui()['valid']
        c['instance'].setPlainText('<a attr="x"><!-- start\ncontinued\n--></a>')
        for highlighter in c['highlighters']:
            highlighter.rehighlight()
        assert c['status'].text() == 'Edited; validate to check'
    finally:
        h.close()


@pytest.mark.parametrize('title', ['Single Thread Chat', 'Worker Thread Chat', 'Queued Worker Chat'])
def test_chat_wrapper_sends_and_displays_a_message(title, qt, monkeypatch):
    from fontlab_python_lessons import network_demos
    m = load(ROOT / f'Scripts/Network/{title}.py')
    class ChatSocket(Datagram):
        def recvfrom(self, size):
            if not self.packets:
                raise TimeoutError()
            return super().recvfrom(size)
        def sendto(self, data, endpoint):
            sockets[0].packets.append(data)
            return len(data)
    sockets = []
    def make(*args):
        item = ChatSocket()
        sockets.append(item)
        return item
    monkeypatch.setattr(network_demos.socket, 'socket', make)
    h = launch_and_build(monkeypatch, m, qt)
    try:
        c = h.controls
        c['name'].setText('Reader')
        c['message'].setText('A local 曲線')
        c['send'].click()
        deadline = time.monotonic() + 1
        while h.inspect_ui()['received'] == 0 and time.monotonic() < deadline:
            c['poll']()
        assert c['messages'].toPlainText() == 'Reader: A local 曲線'
        assert h.inspect_ui()['sent'] == 1
    finally:
        h.close()
