# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/1ca857d797199ecf.md
# this_file: ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py
TITLE = "Flow canvas"
MAIN = True

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


def boundary_point(center, toward, polygon):
    """Intersect a ray from the center with the first polygon edge."""
    x, y = center
    dx, dy = toward[0] - x, toward[1] - y
    if abs(dx) + abs(dy) < 1e-9:
        return center
    nearest = None
    for (ax, ay), (bx, by) in zip(polygon, polygon[1:] + polygon[:1]):
        ex, ey = bx - ax, by - ay
        cross = dx * ey - dy * ex
        if abs(cross) < 1e-9:
            continue
        t = ((ax - x) * ey - (ay - y) * ex) / cross
        u = ((ax - x) * dy - (ay - y) * dx) / cross
        if t >= 0 and 0 <= u <= 1 and (nearest is None or t < nearest):
            nearest = t
    return (x + dx * nearest, y + dy * nearest) if nearest is not None else center


def configure(s):
    gui, core = s.gui, s.core
    nodes = {}
    links = []
    serial = [0]
    labels = []
    s.state.update(
        mode="Pointer",
        shape=0,
        node_color="#a1c9cf",
        line_color="#34466d",
        text_color="#354137",
        zoom=1.0,
    )
    shapes = [
        [(-55, -32), (55, -32), (55, 32), (-55, 32)],
        [(0, -44), (64, 0), (0, 44), (-64, 0)],
        [(-40, -32), (64, -32), (40, 32), (-64, 32)],
        [
            (-44, -32),
            (44, -32),
            (62, -10),
            (62, 10),
            (44, 32),
            (-44, 32),
            (-62, 10),
            (-62, -10),
        ],
    ]

    class Node(gui.QGraphicsPolygonItem):
        def itemChange(self, change, new_value):
            result = gui.QGraphicsPolygonItem.itemChange(self, change, new_value)
            if change == gui.QGraphicsItem.ItemPositionHasChanged:
                update_links()
            return result

    class Label(gui.QGraphicsTextItem):
        def focusOutEvent(self, event):
            gui.QGraphicsTextItem.focusOutEvent(self, event)
            self.setTextInteractionFlags(core.Qt.NoTextInteraction)
            if not str(self.toPlainText()).strip():
                scene.removeItem(self)
                if self in labels:
                    labels.remove(self)
                self.deleteLater()

    def node_at(point):
        x, y = float(point.x()), float(point.y())
        for key, entry in reversed(list(nodes.items())):
            pos = entry["item"].pos()
            if abs(x - float(pos.x())) < 65 and abs(y - float(pos.y())) < 45:
                return key
        return None

    class Scene(gui.QGraphicsScene):
        def mousePressEvent(self, event):
            point = event.scenePos()
            if s.state["mode"] == "Node":
                add_node(s.state["shape"], float(point.x()), float(point.y()))
                event.accept()
            elif s.state["mode"] == "Text":
                label = Label("Type here")
                label.setTextInteractionFlags(core.Qt.TextEditorInteraction)
                label.setPos(point)
                label.setFlag(gui.QGraphicsItem.ItemIsMovable, True)
                label.setFlag(gui.QGraphicsItem.ItemIsSelectable, True)
                label.setDefaultTextColor(gui.QColor(s.state["text_color"]))
                self.addItem(label)
                labels.append(label)
                label.setFocus()
                event.accept()
            elif s.state["mode"] == "Arrow":
                s.state["arrow_start"] = node_at(point)
                event.accept()
            else:
                gui.QGraphicsScene.mousePressEvent(self, event)

        def mouseReleaseEvent(self, event):
            if s.state["mode"] == "Arrow":
                start = s.state.pop("arrow_start", None)
                end = node_at(event.scenePos())
                if start is not None and end is not None:
                    connect_nodes(start, end)
                event.accept()
            else:
                gui.QGraphicsScene.mouseReleaseEvent(self, event)

    scene = s.keep("scene", Scene(s.window))
    scene.setSceneRect(0.0, 0.0, 1800.0, 1200.0)
    scene.setBackgroundBrush(gui.QBrush(gui.QColor("#f2eee4")))
    view = s.keep("view", gui.QGraphicsView(scene, s.panel))
    view.setRenderHint(gui.QPainter.Antialiasing, True)
    s.layout.addWidget(view)

    def add_node(shape, x, y):
        serial[0] += 1
        key = serial[0]
        item = Node(gui.QPolygonF([core.QPointF(a, b) for a, b in shapes[shape]]))
        item.setData(0, key)
        item.setBrush(gui.QBrush(gui.QColor(s.state["node_color"])))
        for flag in (
            gui.QGraphicsItem.ItemIsMovable,
            gui.QGraphicsItem.ItemIsSelectable,
            gui.QGraphicsItem.ItemSendsGeometryChanges,
        ):
            item.setFlag(flag, True)
        nodes[key] = {"item": item, "shape": shape}
        scene.addItem(item)
        item.setPos(float(x), float(y))
        s.state["nodes"] = len(nodes)
        return key

    def connect_nodes(start, end):
        if start == end or start not in nodes or end not in nodes:
            return False
        pa, pb = nodes[start]["item"].pos(), nodes[end]["item"].pos()
        if (
            math.hypot(float(pa.x()) - float(pb.x()), float(pa.y()) - float(pb.y()))
            < 1e-6
        ):
            return False
        line = gui.QGraphicsLineItem(0.0, 0.0, 1.0, 1.0)
        line.setPen(gui.QPen(gui.QColor(s.state["line_color"]), 2))
        scene.addItem(line)
        arrow = gui.QGraphicsPolygonItem(gui.QPolygonF())
        arrow.setPen(gui.QPen(gui.QColor(s.state["line_color"])))
        arrow.setBrush(gui.QBrush(gui.QColor(s.state["line_color"])))
        scene.addItem(arrow)
        line.setZValue(-1.0)
        arrow.setZValue(-1.0)
        links.append((start, end, line, arrow))
        update_links()
        return True

    def update_links():
        for start, end, line, arrow in links:
            points = []
            for key in (start, end):
                pos = nodes[key]["item"].pos()
                points.append((float(pos.x()), float(pos.y())))
            if math.dist(*points) < 1e-6:
                line.setVisible(False)
                arrow.setVisible(False)
                continue
            ends = []
            for i, key in enumerate((start, end)):
                cx, cy = points[i]
                polygon = [(x + cx, y + cy) for x, y in shapes[nodes[key]["shape"]]]
                ends.append(boundary_point(points[i], points[1 - i], polygon))
            (x, y), (xx, yy) = ends
            line.setVisible(True)
            arrow.setVisible(True)
            line.setLine(x, y, xx, yy)
            angle = math.atan2(yy - y, xx - x)
            arrow.setPolygon(
                gui.QPolygonF(
                    [
                        core.QPointF(xx, yy),
                        core.QPointF(
                            xx - 14 * math.cos(angle - 0.4),
                            yy - 14 * math.sin(angle - 0.4),
                        ),
                        core.QPointF(
                            xx - 14 * math.cos(angle + 0.4),
                            yy - 14 * math.sin(angle + 0.4),
                        ),
                    ]
                )
            )
        s.state["links"] = len(links)

    def selected_nodes():
        return [item.data(0) for item in scene.selectedItems() if item.data(0) in nodes]

    def delete_selected():
        keys = selected_nodes()
        for entry in list(links):
            if entry[0] in keys or entry[1] in keys:
                scene.removeItem(entry[2])
                scene.removeItem(entry[3])
                entry[2].delete()
                entry[3].delete()
                links.remove(entry)
        for key in keys:
            item = nodes.pop(key)["item"]
            scene.removeItem(item)
            item.delete()
        for item in scene.selectedItems():
            scene.removeItem(item)
            if item in labels:
                labels.remove(item)
            item.delete()
        s.state["nodes"] = len(nodes)
        update_links()

    def color(kind):
        dialog = gui.QColorDialog(gui.QColor(s.state[kind]), s.window)

        def chosen(color):
            s.state[kind] = str(color.name())
            if kind == "node_color":
                for key in selected_nodes():
                    nodes[key]["item"].setBrush(gui.QBrush(color))
            elif kind == "line_color":
                for _, _, line, arrow in links:
                    line.setPen(gui.QPen(color, 2))
                    arrow.setBrush(gui.QBrush(color))
                    arrow.setPen(gui.QPen(color))
            else:
                for item in scene.selectedItems():
                    if item.inherits("QGraphicsTextItem"):
                        item.setDefaultTextColor(color)

        s.connect(dialog, "colorSelected(QColor)", chosen)
        s.dialog(dialog)

    s.combo(
        "Mode",
        ["Pointer", "Node", "Arrow", "Text"],
        lambda i: s.state.update(mode=["Pointer", "Node", "Arrow", "Text"][i]),
    )
    s.combo(
        "Shape",
        ["Process", "Decision", "Input", "Terminator"],
        lambda i: s.state.update(shape=i, mode="Node"),
    )
    s.combo(
        "Background",
        ["Paper", "Blue", "Green"],
        lambda i: scene.setBackgroundBrush(
            gui.QBrush(gui.QColor(["#f2eee4", "#e4edf3", "#e4eee4"][i]))
        ),
    )
    s.combo(
        "Zoom",
        ["50%", "75%", "100%", "125%", "150%"],
        lambda i: (
            view.resetTransform(),
            view.scale([0.5, 0.75, 1, 1.25, 1.5][i], [0.5, 0.75, 1, 1.25, 1.5][i]),
        ),
    )
    toolbar = s.window.addToolBar("Edit")
    menu = s.window.menuBar().addMenu("Item")
    s.action(menu, "Delete", delete_selected)
    for kind in ("node_color", "line_color", "text_color"):
        toolbar.addAction(s.action(menu, kind, lambda k=kind: color(k)))

    def stack(delta):
        for item in scene.selectedItems():
            item.setZValue(float(value(item, "zValue")) + delta)

    s.action(menu, "Bring forward", lambda: stack(1))
    s.action(menu, "Send back", lambda: stack(-1))
    font = s.keep("Font", gui.QFontComboBox(s.panel))
    s.layout.addWidget(font)
    s.connect(
        font,
        "currentFontChanged(QFont)",
        lambda chosen: [
            item.setFont(chosen)
            for item in scene.selectedItems()
            if hasattr(item, "setFont")
        ],
    )
    s.action(s.window.menuBar().addMenu("File"), "Exit", s.handle.close)
    s.action(
        s.window.menuBar().addMenu("Help"),
        "About",
        lambda: s.message("Build a flow using nodes, connectors and text."),
    )
    for key, obj in {
        "nodes": nodes,
        "links": links,
        "labels": labels,
        "add_node": add_node,
        "connect_nodes": connect_nodes,
        "update_links": update_links,
        "delete_selected": delete_selected,
    }.items():
        s.keep(key, obj)
