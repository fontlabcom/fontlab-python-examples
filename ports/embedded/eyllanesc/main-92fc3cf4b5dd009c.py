# this_file: ports/embedded/eyllanesc/main-92fc3cf4b5dd009c.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/embedded/lightmaps/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-


# Reuses the credited existing official port; its notices above remain applicable.
import math
from pathlib import Path
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.official import Demo, read


def build(qt: Any) -> ExampleHandle:
    demo = Demo(qt, __file__, "92fc3cf4b5dd009c")
    QAction = qt.QtGui.QAction
    QBasicTimer = qt.QtCore.QBasicTimer
    QColor = qt.QtGui.QColor
    QImage = qt.QtGui.QImage
    QMainWindow = qt.QtGui.QMainWindow
    QNetworkAccessManager = qt.QtNetwork.QNetworkAccessManager
    QNetworkRequest = qt.QtNetwork.QNetworkRequest
    QObject = qt.private.QObject
    QPainter = qt.QtGui.QPainter
    QPainterPath = qt.QtGui.QPainterPath
    QPixmap = qt.QtGui.QPixmap
    QPoint = qt.QtCore.QPoint
    QPointF = qt.QtCore.QPointF
    QRect = qt.QtCore.QRect
    QUrl = qt.QtCore.QUrl
    QWidget = qt.QtGui.QWidget
    Qt = qt.QtCore.Qt
    QObject = qt.private.QObject
    try:
        import time

        from fontlab_python_examples.official import LocalServer

        def serve_http(connection, stop, publish):
            request = bytearray()
            deadline = time.monotonic() + 1
            while b"\r\n\r\n" not in request and len(request) < 65536:
                if stop.is_set() or time.monotonic() > deadline:
                    return
                try:
                    data = connection.recv(4096)
                except TimeoutError:
                    continue
                if not data:
                    return
                request.extend(data)
            path = bytes(request).split(b" ")[1] if b" " in request else b"/"
            body = payload
            status = b"200 OK"
            if path == b"/missing":
                status = b"404 Not Found"
                body = b"Missing owned file"
            connection.sendall(
                b"HTTP/1.1 "
                + status
                + b"\r\nContent-Type: "
                + content_type
                + b"\r\nContent-Length: "
                + str(len(body)).encode()
                + b"\r\nConnection: close\r\n\r\n"
                + body
            )
            publish(("served", len(body)))

        payload = b""
        content_type = b"image/png"
        endpoint = None
        HOLD_TIME = 701
        MAX_MAGNIFIER = 229
        TDIM = 256

        def tileForCoordinate(lat, lng, zoom):
            zn = float(1 << zoom)
            tx = float(lng + 180.0) / 360.0
            ty = (
                1.0
                - math.log(
                    math.tan(lat * math.pi / 180.0)
                    + 1.0 / math.cos(lat * math.pi / 180.0)
                )
                / math.pi
            ) / 2.0
            return QPointF(tx * zn, ty * zn)

        def longitudeFromTile(tx, zoom):
            zn = float(1 << zoom)
            lat = tx / zn * 360.0 - 180.0
            return lat

        def latitudeFromTile(ty, zoom):
            zn = float(1 << zoom)
            n = math.pi - 2 * math.pi * ty / zn
            lng = 180.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(0 - n)))
            return lng

        class SlippyMap(QObject):
            def __init__(self, parent=None):
                QObject.__init__(self, parent)
                self._offset = QPoint()
                self._tilesRect = QRect()
                self._tilePixmaps = {}
                self._manager = QNetworkAccessManager(self)
                self._manager.setProxy(
                    qt.QtNetwork.QNetworkProxy(qt.QtNetwork.QNetworkProxy.NoProxy)
                )
                self._url = QUrl()
                self.width = 400
                self.height = 300
                self.zoom = 15
                self.latitude = 59.9138204
                self.longitude = 10.7387413
                self._emptyTile = QPixmap(TDIM, TDIM)
                self._emptyTile.fill(QColor(Qt.lightGray))
                self.pendingReply = None
                demo.track(
                    self,
                    "_emptyTile",
                    "_manager",
                    "_offset",
                    "_tilePixmaps",
                    "_tilesRect",
                    "_url",
                    "height",
                    "latitude",
                    "longitude",
                    "pendingReply",
                    "pendingTile",
                    "width",
                    "zoom",
                )

                demo.connect(
                    self._manager, "finished(QNetworkReply*)", self.handleNetworkData
                )
                demo.handle.cleanup.append(self.stop)

            def invalidate(self):
                if self.width <= 0 or self.height <= 0 or demo.closing:
                    return
                ct = tileForCoordinate(self.latitude, self.longitude, self.zoom)
                tx, ty = (read(ct, "x"), read(ct, "y"))
                xp = int(self.width / 2 - (tx - math.floor(tx)) * TDIM)
                yp = int(self.height / 2 - (ty - math.floor(ty)) * TDIM)
                xa, ya = ((xp + TDIM - 1) // TDIM, (yp + TDIM - 1) // TDIM)
                xs, ys = (int(tx) - xa, int(ty) - ya)
                xe, ye = (
                    int(tx) + (self.width - xp - 1) // TDIM,
                    int(ty) + (self.height - yp - 1) // TDIM,
                )
                self._offset = QPoint(int(xp - xa * TDIM), int(yp - ya * TDIM))
                self._tilesRect = QRect(xs, ys, xe - xs + 1, ye - ys + 1)
                if self.pendingReply is None:
                    self.download()
                self.parent().update(QRect(0, 0, self.width, self.height))

            def render(self, painter, rect):
                for x in range(read(self._tilesRect, "width")):
                    for y in range(read(self._tilesRect, "height")):
                        tp = (x + self._tilesRect.left(), y + self._tilesRect.top())
                        box = self.tileRect(tp)
                        if rect.intersects(box):
                            painter.drawPixmap(
                                box,
                                self._tilePixmaps.get(
                                    (self.zoom, *tp), self._emptyTile
                                ),
                            )

            def pan(self, delta):
                center = tileForCoordinate(self.latitude, self.longitude, self.zoom)
                self.latitude = latitudeFromTile(
                    read(center, "y") - read(delta, "y") / TDIM, self.zoom
                )
                self.longitude = longitudeFromTile(
                    read(center, "x") - read(delta, "x") / TDIM, self.zoom
                )
                self.invalidate()

            def handleNetworkData(self, reply):
                if demo.closing:
                    return
                tp = self.pendingTile
                image = QImage()
                if not reply.error() and image.loadFromData(reply.readAll(), "PNG"):
                    self._tilePixmaps[tp] = QPixmap.fromImage(image)
                else:
                    self._tilePixmaps[tp] = self._emptyTile
                    demo.error = reply.errorString()
                self.pendingReply = None
                reply.deleteLater()
                bound = self._tilesRect.adjusted(-2, -2, 2, 2)
                for key in list(self._tilePixmaps):
                    if key[0] != self.zoom or not bound.contains(
                        QPoint(int(key[1]), int(key[2]))
                    ):
                        del self._tilePixmaps[key]
                self.parent().update(self.tileRect(tp[1:]))
                self.download()

            def download(self):
                if demo.closing:
                    return
                grab = None
                for x in range(read(self._tilesRect, "width")):
                    for y in range(read(self._tilesRect, "height")):
                        tp = (
                            self.zoom,
                            x + self._tilesRect.left(),
                            y + self._tilesRect.top(),
                        )
                        if tp not in self._tilePixmaps:
                            grab = tp
                            break
                    if grab is not None:
                        break
                if grab is None:
                    return
                self.pendingTile = grab
                path = "http://127.0.0.1:{:d}/{:d}/{:d}/{:d}.png".format(
                    endpoint.port, *grab
                )
                endpoint.validate_url(path)
                request = QNetworkRequest(QUrl(path))
                request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, False)
                self.pendingReply = self._manager.get(request)

            def tileRect(self, tp):
                x = (tp[0] - self._tilesRect.left()) * TDIM + read(self._offset, "x")
                y = (tp[1] - self._tilesRect.top()) * TDIM + read(self._offset, "y")
                return QRect(x, y, TDIM, TDIM)

            def stop(self):
                if self.pendingReply is not None:
                    self.pendingReply.abort()

        class LightMaps(QWidget):
            def __init__(self, parent=None):
                QWidget.__init__(self, parent)
                demo.track(
                    self,
                    "_largeMap",
                    "_normalMap",
                    "dragPos",
                    "invert",
                    "maskPixmap",
                    "pressPos",
                    "pressed",
                    "snapped",
                    "tapTimer",
                    "zoomPixmap",
                    "zoomed",
                )
                self.pressed = False
                self.snapped = False
                self.zoomed = False
                self.invert = False
                self._normalMap = demo.remember("normalMap", SlippyMap(self))
                self._largeMap = demo.remember("largeMap", SlippyMap(self))
                self.pressPos = demo.remember("pressPos", QPoint())
                self.dragPos = demo.remember("dragPos", QPoint())
                self.tapTimer = demo.remember("tapTimer", QBasicTimer())
                self.zoomPixmap = demo.remember("zoomPixmap", QPixmap())
                self.maskPixmap = demo.remember("maskPixmap", QPixmap())
                demo.handle.cleanup.append(self.tapTimer.stop)

            def setCenter(self, lat, lng):
                self._normalMap.latitude = lat
                self._normalMap.longitude = lng
                self._normalMap.invalidate()
                self._largeMap.invalidate()

            def toggleNightMode(self):
                self.invert = not self.invert
                self.update()

            def updateMap(self, r):
                self.update(r)

            def activateZoom(self):
                self.zoomed = True
                self.tapTimer.stop()
                self._largeMap.zoom = self._normalMap.zoom + 1
                self._largeMap.width = self._normalMap.width * 2
                self._largeMap.height = self._normalMap.height * 2
                self._largeMap.latitude = self._normalMap.latitude
                self._largeMap.longitude = self._normalMap.longitude
                self._largeMap.invalidate()
                self.update()

            def resizeEvent(self, event):
                self._normalMap.width = read(self, "width")
                self._normalMap.height = read(self, "height")
                self._normalMap.invalidate()
                self._largeMap.width = self._normalMap.width * 2
                self._largeMap.height = self._normalMap.height * 2
                self._largeMap.invalidate()

            def paintEvent(self, event):
                if demo.closing:
                    return
                if self.zoomed:
                    dim = min(read(self, "width"), read(self, "height"))
                    magnifierSize = int(min(MAX_MAGNIFIER, dim * 2 / 3))
                    radius = magnifierSize // 2
                    ring = radius - 15
                    if (
                        read(self.maskPixmap, "width") != magnifierSize
                        or read(self.maskPixmap, "height") != magnifierSize
                    ):
                        self.maskPixmap = QPixmap(magnifierSize, magnifierSize)
                        self.maskPixmap.fill(QColor(Qt.transparent))
                        gradient = qt.QtGui.QRadialGradient(radius, radius, radius)
                        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
                        gradient.setColorAt(0.5, QColor(128, 128, 128, 255))
                        mask = QPainter(self.maskPixmap)
                        try:
                            mask.setRenderHint(QPainter.Antialiasing)
                            mask.setCompositionMode(QPainter.CompositionMode_Source)
                            mask.setBrush(qt.QtGui.QBrush(gradient))
                            mask.setPen(Qt.NoPen)
                            mask.drawRect(self.maskPixmap.rect())
                            mask.setBrush(qt.QtGui.QBrush(QColor(Qt.transparent)))
                            mask.drawEllipse(QPointF(radius, radius), ring, ring)
                        finally:
                            mask.end()
                    center = QPoint(
                        read(self.dragPos, "x"), read(self.dragPos, "y") - radius // 2
                    )
                    corner = QPoint(
                        read(center, "x") - radius, read(center, "y") - radius
                    )
                    xy = QPoint(
                        read(center, "x") * 2 - radius, read(center, "y") * 2 - radius
                    )
                    if (
                        read(self.zoomPixmap, "width") != magnifierSize
                        or read(self.zoomPixmap, "height") != magnifierSize
                    ):
                        self.zoomPixmap = QPixmap(magnifierSize, magnifierSize)
                        self.zoomPixmap.fill(QColor(Qt.lightGray))
                    enlarged = QPainter(self.zoomPixmap)
                    try:
                        enlarged.translate(0 - read(xy, "x"), 0 - read(xy, "y"))
                        self._largeMap.render(
                            enlarged,
                            QRect(
                                read(xy, "x"),
                                read(xy, "y"),
                                magnifierSize,
                                magnifierSize,
                            ),
                        )
                    finally:
                        enlarged.end()
                painter = QPainter(self)
                try:
                    self._normalMap.render(painter, event.rect())
                    painter.setPen(QColor(Qt.black))
                    painter.drawText(
                        read(self, "rect"),
                        Qt.AlignBottom | Qt.TextWordWrap,
                        "Owned offline tile fixture; original OpenStreetMap viewer",
                    )
                    if self.zoomed:
                        clip = QPainterPath()
                        clip.addEllipse(QPointF(center), ring, ring)
                        painter.setRenderHint(QPainter.Antialiasing)
                        painter.setClipPath(clip)
                        painter.drawPixmap(corner, self.zoomPixmap)
                        painter.setClipping(False)
                        painter.drawPixmap(corner, self.maskPixmap)
                        painter.setPen(QColor(Qt.gray))
                        painter.drawPath(clip)
                    if self.invert:
                        painter.setCompositionMode(QPainter.CompositionMode_Difference)
                        painter.fillRect(event.rect(), QColor(Qt.white))
                finally:
                    painter.end()

            def timerEvent(self, event):
                if not self.zoomed:
                    self.activateZoom()
                self.update()

            def mousePressEvent(self, event):
                if event.buttons() != Qt.LeftButton:
                    return
                self.pressed = self.snapped = True
                self.pressPos = self.dragPos = read(event, "pos")
                self.tapTimer.stop()
                self.tapTimer.start(HOLD_TIME, Qt.CoarseTimer, self)

            def mouseMoveEvent(self, event):
                if not event.buttons():
                    return
                if not self.zoomed:
                    if not self.pressed or not self.snapped:
                        delta = QPoint(
                            read(read(event, "pos"), "x") - read(self.pressPos, "x"),
                            read(read(event, "pos"), "y") - read(self.pressPos, "y"),
                        )
                        self.pressPos = read(event, "pos")
                        self._normalMap.pan(delta)
                        return
                    else:
                        threshold = 10
                        delta = QPoint(
                            read(read(event, "pos"), "x") - read(self.pressPos, "x"),
                            read(read(event, "pos"), "y") - read(self.pressPos, "y"),
                        )
                        if self.snapped:
                            self.snapped &= read(delta, "x") < threshold
                            self.snapped &= read(delta, "y") < threshold
                            self.snapped &= read(delta, "x") > (0 - threshold)
                            self.snapped &= read(delta, "y") > (0 - threshold)
                        if not self.snapped:
                            self.tapTimer.stop()
                else:
                    self.dragPos = read(event, "pos")
                    self.update()

            def mouseReleaseEvent(self, event):
                self.tapTimer.stop()
                self.zoomed = False
                self.update()

            def keyPressEvent(self, event):
                if not self.zoomed:
                    if read(event, "key") == Qt.Key_Left:
                        self._normalMap.pan(QPoint(20, 0))
                    if read(event, "key") == Qt.Key_Right:
                        self._normalMap.pan(QPoint((-20), 0))
                    if read(event, "key") == Qt.Key_Up:
                        self._normalMap.pan(QPoint(0, 20))
                    if read(event, "key") == Qt.Key_Down:
                        self._normalMap.pan(QPoint(0, (-20)))
                    if (
                        read(event, "key") == Qt.Key_Z
                        or read(event, "key") == Qt.Key_Select
                    ):
                        self.dragPos = demo.remember(
                            "dragPos",
                            QPoint(
                                int(read(self, "width") / 2),
                                int(read(self, "height") / 2),
                            ),
                        )
                        self.activateZoom()
                else:
                    if (
                        read(event, "key") == Qt.Key_Z
                        or read(event, "key") == Qt.Key_Select
                    ):
                        self.zoomed = False
                        self.update()
                    delta = demo.remember("delta", QPoint(0, 0))
                    if read(event, "key") == Qt.Key_Left:
                        delta = demo.remember("delta", QPoint((-15), 0))
                    if read(event, "key") == Qt.Key_Right:
                        delta = demo.remember("delta", QPoint(15, 0))
                    if read(event, "key") == Qt.Key_Up:
                        delta = demo.remember("delta", QPoint(0, (-15)))
                    if read(event, "key") == Qt.Key_Down:
                        delta = demo.remember("delta", QPoint(0, 15))
                    if delta != QPoint(0, 0):
                        self.dragPos = QPoint(
                            read(self.dragPos, "x") + read(delta, "x"),
                            read(self.dragPos, "y") + read(delta, "y"),
                        )
                        self.update()

        class MapZoom(QMainWindow):
            def __init__(self):
                QMainWindow.__init__(self, None)
                demo.begin(self)
                nonlocal payload, endpoint
                tile = QPixmap(TDIM, TDIM)
                tile.fill(QColor(Qt.lightGray))
                painter = QPainter(tile)
                try:
                    painter.setPen(qt.QtGui.QColor(Qt.darkGray))
                    painter.drawRect(1, 1, TDIM - 2, TDIM - 2)
                    painter.drawText(20, 40, "Owned offline tile")
                finally:
                    painter.end()
                path = Path(demo.temp_dir()) / "tile.png"
                if not tile.save(str(path), "PNG"):
                    raise OSError("Cannot save owned tile")
                payload = path.read_bytes()
                endpoint = LocalServer(demo, serve_http)
                demo.track(
                    self,
                    "berlinAction",
                    "jakartaAction",
                    "map_",
                    "nightModeAction",
                    "osloAction",
                    "osmAction",
                )
                self.map_ = demo.remember("map_", LightMaps(self))
                self.setCentralWidget(self.map_)
                self.map_.setFocus()
                self.osloAction = demo.remember("osloAction", QAction("&Oslo", self))
                self.berlinAction = demo.remember(
                    "berlinAction", QAction("&Berlin", self)
                )
                self.jakartaAction = demo.remember(
                    "jakartaAction", QAction("&Jakarta", self)
                )
                self.nightModeAction = demo.remember(
                    "nightModeAction", QAction("Night Mode", self)
                )
                self.nightModeAction.setCheckable(True)
                self.nightModeAction.setChecked(False)
                self.osmAction = demo.remember(
                    "osmAction", QAction("About OpenStreetMap", self)
                )
                demo.connect(self.osloAction, "triggered()", self.chooseOslo)
                demo.connect(self.berlinAction, "triggered()", self.chooseBerlin)
                demo.connect(self.jakartaAction, "triggered()", self.chooseJakarta)
                demo.connect(
                    self.nightModeAction, "triggered()", self.map_.toggleNightMode
                )
                demo.connect(self.osmAction, "triggered()", self.aboutOsm)
                menu = self.menuBar().addMenu("&Options")
                menu.addAction(self.osloAction)
                menu.addAction(self.berlinAction)
                menu.addAction(self.jakartaAction)
                menu.addSeparator()
                menu.addAction(self.nightModeAction)
                menu.addAction(self.osmAction)

            def chooseOslo(self):
                self.map_.setCenter(59.9138204, 10.7387413)

            def chooseBerlin(self):
                self.map_.setCenter(52.52958999943302, 13.383053541183472)

            def chooseJakarta(self):
                self.map_.setCenter(-6.211544, 106.845172)

            def aboutOsm(self):
                demo.message(
                    self,
                    "About OpenStreetMap",
                    "Original map viewer by Qt/PyQt. This port serves only an owned offline tile fixture; geographic tiles require a separate licensed local dataset.",
                )

        window = MapZoom()
        window.setWindowTitle("Light Maps")
        window.resize(600, 450)
        demo.remember("map", window.map_)
        demo.remember("pan", window.map_._normalMap.pan)
        demo.remember("activateZoom", window.map_.activateZoom)
        return demo.finish(
            window,
            lambda: {
                "endpoint": endpoint.snapshot(),
                "latitude": window.map_._normalMap.latitude,
                "longitude": window.map_._normalMap.longitude,
                "zoom": window.map_._normalMap.zoom,
                "zoomed": window.map_.zoomed,
                "night_mode": window.map_.invert,
                "tile_count": len(window.map_._normalMap._tilePixmaps),
            },
        )
    except BaseException:
        demo.abort()
        raise


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("92fc3cf4b5dd009c")
