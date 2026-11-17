# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/d8803c2afaabf3d5.md
# this_file: Scripts/Network/Local Tile Map.py
"""Local Tile Map with an owned local peer; no external server or font needed."""
from fontlab_python_lessons import qt_demos as S
from fontlab_python_lessons.qt_demos import value
from fontlab_python_lessons.network_demos import (
    Session, http_peer, local_url, network_manager, request_for, retire_reply, mercator,
)

TITLE = "Local schematic map"
MAIN = False

def configure(s):
    gui, core = s.gui, s.core
    peer = http_peer(s)
    manager = network_manager(s)
    cache = {}
    replies = {}
    presets = [
        ("Harbour", 53.4, -3.0),
        ("Hill town", 45.7, 7.7),
        ("Garden city", 35.7, 139.7),
    ]
    s.state.update(
        zoom=5,
        center=list(mercator(53.4, -3.0, 5)),
        night=False,
        magnifier=False,
        requests=0,
        cache=0,
    )
    pointer = [core.QPoint(200, 180)]
    drag_origin = [None]

    def request_tile(x, y):
        key = (x % (2 ** s.state["zoom"]), max(0, min(2 ** s.state["zoom"] - 1, y)))
        if key in cache or key in replies:
            return
        text = (
            "http://"
            + peer.host
            + ":"
            + str(peer.port)
            + "/tile/"
            + str(key[0])
            + "/"
            + str(key[1])
        )
        local_url(text, peer)
        reply = manager.get(request_for(s, text))
        replies[key] = reply
        s.state["requests"] += 1

        def done():
            if replies.get(key) is not reply:
                return
            if not reply.error() and not reply.attribute(
                s.qt.QtNetwork.QNetworkRequest.RedirectionTargetAttribute
            ):
                image = gui.QImage()
                if image.loadFromData(core.QByteArray(reply.readAll().data()), "PNG"):
                    cache[key] = gui.QPixmap.fromImage(image)
            replies.pop(key, None)
            retire_reply(s, reply)
            s.state["cache"] = len(cache)
            canvas.update()

        s.connect(reply, "finished()", done)

    def fetch():
        cx, cy = s.state["center"]
        for dy in range(-2, 3):
            for dx in range(-3, 4):
                request_tile(int(cx) + dx, int(cy) + dy)

    def pan(dx, dy):
        center = s.state["center"]
        center[0] += dx / 128
        center[1] += dy / 128
        center[1] = max(0, min(2 ** s.state["zoom"] - 1, center[1]))
        fetch()
        canvas.update()

    class Canvas(gui.QWidget):
        def paintEvent(self, event):
            gui.QWidget.paintEvent(self, event)
            p = gui.QPainter(self)
            try:
                p.fillRect(
                    value(self, "rect"),
                    gui.QColor("#172535" if s.state["night"] else "#dce8df"),
                )
                cx, cy = s.state["center"]
                for (x, y), picture in cache.items():
                    px = (x - cx) * 128 + int(value(self, "width")) / 2
                    py = (y - cy) * 128 + int(value(self, "height")) / 2
                    p.drawPixmap(int(px), int(py), 128, 128, picture)
                if s.state["night"]:
                    p.fillRect(value(self, "rect"), gui.QColor(0, 20, 55, 110))
                if s.state["magnifier"]:
                    x, y = float(pointer[0].x()), float(pointer[0].y())
                    p.save()
                    clip = gui.QPainterPath()
                    clip.addEllipse(core.QPointF(x, y), 80.0, 80.0)
                    p.setClipPath(clip)
                    p.translate(x, y)
                    p.scale(2.0, 2.0)
                    p.translate(-x, -y)
                    for (tx, ty), picture in cache.items():
                        p.drawPixmap(
                            int((tx - cx) * 128 + int(value(self, "width")) / 2),
                            int((ty - cy) * 128 + int(value(self, "height")) / 2),
                            128,
                            128,
                            picture,
                        )
                    p.restore()
                    feather = gui.QRadialGradient(x, y, 84.0)
                    feather.setColorAt(0.8, gui.QColor(255, 255, 255, 0))
                    feather.setColorAt(1.0, gui.QColor(40, 50, 60, 180))
                    p.setBrush(gui.QBrush(feather))
                    p.drawEllipse(core.QPointF(x, y), 84.0, 84.0)
            except Exception as error:
                print("Map painting failed:", error)
            finally:
                p.end()

        def mousePressEvent(self, event):
            pointer[0] = event.pos()
            drag_origin[0] = event.pos()
            hold.start(400)

        def mouseMoveEvent(self, event):
            if drag_origin[0] is not None:
                point = event.pos()
                old = drag_origin[0]
                dx, dy = int(old.x()) - int(point.x()), int(old.y()) - int(point.y())
                if abs(dx) + abs(dy) > 2:
                    hold.stop()
                    s.state["magnifier"] = False
                pan(dx, dy)
                drag_origin[0] = point
                pointer[0] = point

        def mouseReleaseEvent(self, event):
            hold.stop()
            drag_origin[0] = None
            s.state["magnifier"] = False
            self.update()

        def keyPressEvent(self, event):
            moves = {
                core.Qt.Key_Left: (-64, 0),
                core.Qt.Key_Right: (64, 0),
                core.Qt.Key_Up: (0, -64),
                core.Qt.Key_Down: (0, 64),
            }
            if event.key() in moves:
                pan(*moves[event.key()])
                event.accept()
            else:
                gui.QWidget.keyPressEvent(self, event)

    canvas = s.keep("map", Canvas(s.panel))
    canvas.setMinimumSize(560, 360)
    canvas.setFocusPolicy(core.Qt.StrongFocus)
    s.layout.addWidget(canvas)

    def magnify():
        s.state["magnifier"] = True
        canvas.update()

    hold = s.timer("hold", magnify, 400, start=False, once=True)

    def city(index):
        _, lat, lon = presets[index]
        s.state["center"] = list(mercator(lat, lon, s.state["zoom"]))
        fetch()
        canvas.update()

    s.combo("City", [entry[0] for entry in presets], city)

    def night():
        s.state["night"] = not s.state["night"]
        canvas.update()

    s.button("Night", night)
    s.button(
        "Information",
        lambda: s.message(
            "Illustrative map tiles served by this example's local peer."
        ),
    )

    def cancel_replies():
        for reply in list(replies.values()):
            reply.abort()
        replies.clear()

    s.handle.cleanup.append(cancel_replies)
    s.keep("pan", pan)
    s.keep("city", city)
    s.keep("fetch", fetch)
    s.keep("cache", cache)
    s.timer("initial_tiles", fetch, 0, once=True)

def build(qt):
    with Session(qt, TITLE, MAIN) as session:
        configure(session)
        return session.finish()


def main():
    return S.launch(build, 'restored_lightmaps-d8803c2afaabf3d5', 'Local Tile Map')


if __name__ == "__main__":
    main()
