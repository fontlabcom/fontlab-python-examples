# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/fcfaf9667206bbd6.md
# this_file: ports/graphicsview/pyqt-official/collidingmice-fcfaf9667206bbd6.py
TITLE = "Moving scene"
MAIN = False
KIND = "mice"

from pathlib import Path
from tempfile import TemporaryDirectory

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    result = getattr(obj, name)
    return result() if callable(result) else result


class Session:
    """One example lifetime; Python state stays off native wrappers."""

    def __init__(self, qt, title, main=False):
        self.qt, self.gui, self.core = qt, qt.QtGui, qt.QtCore
        self.state = {}
        self.pending = []
        self.temporary = None
        self.closing = False
        self.before_close = None
        session = self
        base = self.gui.QMainWindow if main else self.gui.QWidget

        class Window(base):
            def closeEvent(self, event):
                if session.state.get("dragging", False):
                    event.ignore()
                    return
                if session.closing:
                    event.accept()
                elif session.before_close:
                    event.ignore()
                    session.before_close()
                else:
                    event.ignore()
                    session.handle.close()

        self.window = Window()
        self.window.setWindowTitle(title)
        self.window.setAttribute(self.core.Qt.WA_QuitOnClose, False)
        self.window.setAttribute(self.core.Qt.WA_DeleteOnClose, False)
        self.window.resize(760, 560)
        self.handle = ExampleHandle(self.window, self.snapshot)
        self.handle.controls["controller"] = self
        self.handle.cleanup.append(self.prepare_close)
        self.handle.after_close.append(self.dispose)
        self.panel = self.gui.QWidget(self.window) if main else self.window
        if main:
            self.window.setCentralWidget(self.panel)
        self.layout = self.gui.QVBoxLayout(self.panel)

    def snapshot(self):
        return dict(self.state)

    def prepare_close(self):
        if self.state.get("dragging", False):
            raise RuntimeError("Finish the drag before closing this example")
        self.closing = True

    def dispose(self):
        if self.temporary is not None:
            self.temporary.cleanup()
            self.temporary = None
        self.pending.clear()

    def keep(self, name, obj):
        self.handle.controls[name] = obj
        return obj

    def connect(self, obj, signature, callback):
        def route(*args):
            if not self.closing:
                callback(*args)

        self.handle.connect_old(obj, signature, route)
        return route

    def button(self, name, callback, layout=None):
        button = self.keep(name, self.gui.QPushButton(name, self.panel))
        (layout or self.layout).addWidget(button)
        self.connect(button, "clicked()", lambda *args: callback())
        return button

    def combo(self, name, items, callback, layout=None):
        combo = self.keep(name, self.gui.QComboBox(self.panel))
        combo.addItems(items)
        (layout or self.layout).addWidget(combo)
        self.connect(combo, "currentIndexChanged(int)", lambda i: callback(int(i)))
        return combo

    def timer(self, name, callback, interval, start=True, once=False):
        timer = self.keep(name, self.core.QTimer(self.window))
        timer.setSingleShot(once)
        self.connect(timer, "timeout()", lambda: callback())
        self.handle.cleanup.append(timer.stop)
        if start:
            timer.start(interval)
        return timer

    def root(self):
        if self.temporary is None:
            self.temporary = TemporaryDirectory(prefix="fontlab-example-")
        return Path(self.temporary.name)

    def path(self, filename):
        root = self.root().resolve()
        result = Path(filename).resolve()
        if result == root or not result.is_relative_to(root):
            raise ValueError("Choose a file within the example folder")
        return result

    def dialog(self, dialog):
        from fontlabapp.widgets import OwnedWidget

        dialog.setAttribute(self.core.Qt.WA_QuitOnClose, False)
        self.handle.alerts.append(OwnedWidget(dialog, dialog))
        self.pending.append(dialog)
        dialog.open()
        return dialog

    def message(self, text):
        box = self.gui.QMessageBox(self.window)
        box.setText(str(text))
        return self.dialog(box)

    def choose(self, saving, callback, pattern="All files (*)"):
        box = self.gui.QFileDialog(self.window)
        box.setDirectory(str(self.root()))
        box.setNameFilter(pattern)
        box.setAcceptMode(box.AcceptSave if saving else box.AcceptOpen)

        def selected(filename):
            try:
                callback(str(filename))
            except (OSError, ValueError, UnicodeError) as error:
                self.state["error"] = str(error)
                self.message(str(error))

        self.connect(box, "fileSelected(QString)", selected)
        return self.dialog(box)

    def action(self, menu, name, callback, check=False):
        action = self.keep(name, self.gui.QAction(name, self.window))
        action.setCheckable(check)
        menu.addAction(action)
        self.connect(action, "triggered(bool)", lambda *args: callback())
        return action

    def finish(self):
        return self.handle


def build(qt):
    session = Session(qt, TITLE, MAIN)
    try:
        configure(session)
        return session.finish()
    except BaseException:
        session.handle.close()
        raise


import math
import random


def configure(s):
    gui, core = s.gui, s.core
    scene = s.keep("scene", gui.QGraphicsScene(s.window))
    scene.setSceneRect(-300.0, -250.0, 600.0, 500.0)
    scene.setBackgroundBrush(
        gui.QBrush(gui.QColor("#eee4ae" if KIND == "mice" else "#e2e7e9"))
    )
    nodes = []
    edges = []
    decorations = []
    s.state.update(ticks=0, settled=False, zoom=1.0)

    class View(gui.QGraphicsView):
        def wheelEvent(self, event):
            zoom(1.15 if event.angleDelta().y() > 0 else 1 / 1.15)
            event.accept()

        def keyPressEvent(self, event):
            key = event.key()
            movement = {
                core.Qt.Key_Left: (-20, 0),
                core.Qt.Key_Right: (20, 0),
                core.Qt.Key_Up: (0, -20),
                core.Qt.Key_Down: (0, 20),
            }
            if key in movement and KIND == "elastic":
                point = nodes[4].pos()
                dx, dy = movement[key]
                nodes[4].setPos(float(point.x()) + dx, float(point.y()) + dy)
                timer.start(30)
                s.state["settled"] = False
            elif key in (core.Qt.Key_Space, core.Qt.Key_Return):
                shuffle()
            elif key in (core.Qt.Key_Plus, core.Qt.Key_Equal):
                zoom(1.15)
            elif key == core.Qt.Key_Minus:
                zoom(1 / 1.15)
            else:
                gui.QGraphicsView.keyPressEvent(self, event)

    view = s.keep("view", View(scene, s.panel))
    view.setRenderHint(gui.QPainter.Antialiasing, True)
    s.layout.addWidget(view)

    def zoom(factor):
        if 0.1 < s.state["zoom"] * factor < 5:
            view.scale(factor, factor)
            s.state["zoom"] *= factor

    class Node(gui.QGraphicsEllipseItem):
        def mouseMoveEvent(self, event):
            gui.QGraphicsEllipseItem.mouseMoveEvent(self, event)
            update_edges()
            timer.start(30)
            s.state["settled"] = False

        def mouseReleaseEvent(self, event):
            gui.QGraphicsEllipseItem.mouseReleaseEvent(self, event)
            timer.start(30)

    for i in range(7 if KIND == "mice" else 9):
        node = Node(-16.0, -16.0, 32.0, 32.0)
        node.setFlag(gui.QGraphicsItem.ItemIsMovable, True)
        node.setFlag(gui.QGraphicsItem.ItemIsSelectable, True)
        node.setBrush(
            gui.QBrush(gui.QColor("#a68b77" if KIND == "mice" else "#e7bb46"))
        )
        node.setPos((i % 3 - 1) * 105.0, (i // 3 - 1) * 100.0)
        scene.addItem(node)
        nodes.append(node)
        if KIND == "mice":
            for x in (-17.0, 7.0):
                ear = gui.QGraphicsEllipseItem(x, -24.0, 13.0, 20.0, node)
                ear.setBrush(gui.QBrush(gui.QColor("#cdb3b5")))
            path = gui.QPainterPath()
            path.moveTo(0.0, 14.0)
            path.cubicTo(-20.0, 40.0, 25.0, 40.0, 10.0, 55.0)

            class Tail(gui.QGraphicsItem):
                def __init__(self, parent, drawing=path):
                    gui.QGraphicsItem.__init__(self, parent)
                    self.cr_path = drawing

                def boundingRect(self):
                    return core.QRectF(-25, 10, 60, 50)

                def paint(self, painter, option, widget=None):
                    painter.setPen(gui.QPen(gui.QColor("#957e78"), 2))
                    painter.drawPath(self.cr_path)

            tail = Tail(node)
            decorations.append(tail)
    if KIND == "mice":
        for i in range(28):
            dot = gui.QGraphicsEllipseItem(
                float(i % 7 * 85 - 270), float(i // 7 * 120 - 210), 18.0, 11.0
            )
            dot.setPen(gui.QPen(gui.QColor("#d9c75d")))
            dot.setBrush(gui.QBrush(gui.QColor("#d9c75d")))
            scene.addItem(dot)
            dot.setZValue(-1.0)
    else:
        pairs = [(i, i + 1) for i in range(9) if i % 3 < 2] + [
            (i, i + 3) for i in range(6)
        ]
        for a, b in pairs:
            line = scene.addLine(0.0, 0.0, 0.0, 0.0, gui.QPen(gui.QColor("#536579"), 2))
            arrow = scene.addPolygon(
                gui.QPolygonF(),
                gui.QPen(gui.QColor("#536579")),
                gui.QBrush(gui.QColor("#536579")),
            )
            line.setZValue(-1.0)
            edges.append((a, b, line, arrow))

    def update_edges():
        for a, b, line, arrow in edges:
            pa, pb = nodes[a].pos(), nodes[b].pos()
            x, y = float(pa.x()), float(pa.y())
            dx, dy = float(pb.x()) - x, float(pb.y()) - y
            distance = math.hypot(dx, dy)
            if distance < 0.001:
                line.setVisible(False)
                arrow.setVisible(False)
                continue
            ux, uy = dx / distance, dy / distance
            x1, y1 = x + ux * 17, y + uy * 17
            x2, y2 = x + dx - ux * 17, y + dy - uy * 17
            line.setVisible(True)
            arrow.setVisible(True)
            line.setLine(x1, y1, x2, y2)
            arrow.setPolygon(
                gui.QPolygonF(
                    [
                        core.QPointF(x2, y2),
                        core.QPointF(x2 - ux * 12 + uy * 5, y2 - uy * 12 - ux * 5),
                        core.QPointF(x2 - ux * 12 - uy * 5, y2 - uy * 12 + ux * 5),
                    ]
                )
            )

    headings = [random.random() * math.tau for _ in nodes]

    def tick():
        points = [(float(n.pos().x()), float(n.pos().y())) for n in nodes]
        motion = []
        for i, (x, y) in enumerate(points):
            fx = fy = 0.0
            for j, (other_x, other_y) in enumerate(points):
                if i == j:
                    continue
                dx, dy = x - other_x, y - other_y
                distance = max(1.0, dx * dx + dy * dy)
                if distance == 1 and dx == dy == 0:
                    dx, dy = math.cos(i * 2.4), math.sin(i * 2.4)
                fx += dx * 170 / distance
                fy += dy * 170 / distance
            if KIND == "mice":
                heading = headings[i] + random.uniform(-0.06, 0.06)
                if abs(x) > 245 or abs(y) > 195:
                    heading = math.atan2(-y, -x)
                elif abs(fx) + abs(fy) > 3:
                    heading = math.atan2(fy, fx)
                headings[i] = heading
                fx, fy = math.cos(heading) * 2, math.sin(heading) * 2
                nodes[i].setRotation(math.degrees(heading) + 90)
            else:
                for a, b, _, _ in edges:
                    other = b if a == i else a if b == i else None
                    if other is not None:
                        fx += (points[other][0] - x) * 0.015
                        fy += (points[other][1] - y) * 0.015
                fx = max(-5, min(5, fx))
                fy = max(-5, min(5, fy))
                if abs(fx) + abs(fy) < 0.2:
                    fx = fy = 0
            motion.append((max(-275, min(275, x + fx)), max(-225, min(225, y + fy))))
        for node, (x, y) in zip(nodes, motion):
            node.setPos(x, y)
        update_edges()
        s.state["ticks"] += 1
        if KIND == "elastic" and all(
            abs(a - c) + abs(b - d) < 0.2 for (a, b), (c, d) in zip(points, motion)
        ):
            timer.stop()
            s.state["settled"] = True

    def shuffle():
        for node in nodes:
            node.setPos(random.uniform(-220, 220), random.uniform(-180, 180))
        update_edges()
        timer.start(30)
        s.state["settled"] = False

    timer = s.timer("simulation", tick, 30)
    s.keep("nodes", nodes)
    s.keep("edges", edges)
    s.keep("decorations", decorations)
    s.keep("tick", tick)
    s.keep("shuffle", shuffle)
    s.keep("zoom", zoom)
    update_edges()
