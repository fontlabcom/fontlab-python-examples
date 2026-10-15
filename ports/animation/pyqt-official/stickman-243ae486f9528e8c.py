# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/243ae486f9528e8c.md
# this_file: ports/animation/pyqt-official/stickman-243ae486f9528e8c.py

from contextlib import contextmanager

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    item = getattr(obj, name)
    return item() if callable(item) else item


@contextmanager
def owned(qt, title):
    state = {"closing": False}

    class Window(qt.QtGui.QWidget):
        def closeEvent(self, event):
            if not state["closing"]:
                handle.close()
            event.accept()

    window = Window()
    handle = ExampleHandle(window, dict)
    handle.cleanup.append(lambda: state.update(closing=True))
    try:
        window.setWindowTitle(title)
        window.setAttribute(qt.QtCore.Qt.WA_QuitOnClose, False)
        window.resize(760, 540)
        layout = qt.QtGui.QVBoxLayout(window)
        handle.controls["layout"] = layout
        yield handle, layout
    except BaseException:
        handle.close()
        raise


def wire(handle, obj, signature, callback):
    def receive(*args):
        if not handle.owner.closed:
            callback(*args)

    handle.connect_old(obj, signature, receive)
    return receive


def timer(qt, handle, interval, callback):
    item = qt.QtCore.QTimer(handle.widget)
    wire(handle, item, "timeout()", lambda *args: callback())
    handle.cleanup.append(item.stop)
    item.start(interval)
    return item


import math
import random


def embed(qt, scene, widget):
    proxy = qt.QtGui.QGraphicsProxyWidget()
    proxy.setWidget(widget)
    scene.addItem(proxy)
    return proxy


JOINTS = [
    (0, 0),
    (0, 25),
    (0, 65),
    (0, 100),
    (-25, 30),
    (-40, 60),
    (-50, 85),
    (25, 30),
    (40, 60),
    (50, 85),
    (-18, 105),
    (-22, 145),
    (-25, 180),
    (18, 105),
    (22, 145),
    (25, 180),
]
EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (1, 4),
    (4, 5),
    (5, 6),
    (1, 7),
    (7, 8),
    (8, 9),
    (3, 10),
    (10, 11),
    (11, 12),
    (3, 13),
    (13, 14),
    (14, 15),
]


def keyframe(activity, phase):
    pose = []
    for index, (x, y) in enumerate(JOINTS):
        wave = math.sin(phase * 2 * math.pi + index * 0.4)
        if activity == "jump":
            x, y = (
                x * (1.2 if index in (6, 9) else 1),
                y - 30 * abs(math.sin(phase * math.pi)),
            )
        elif activity == "dance":
            x, y = x + 12 * wave, y + 7 * math.cos(phase * 2 * math.pi)
        elif activity == "dead":
            x, y = y * 0.8 - 60, 170 + x * 0.15
        pose.append((300 + x, 60 + y))
    return pose


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Joint motion studio") as (handle, layout):
        state = {"activity": "rest"}
        scene = gui.QGraphicsScene(handle.widget)
        scene.setSceneRect(0, 0, 640, 420)

        def choose(activity):
            group.stop()
            state["activity"] = activity
            for index, motion in enumerate(motions):
                motion.setStartValue(value(joints[index], "pos"))
                for step in range(1, 5):
                    x, y = keyframe(activity, step / 4)[index]
                    motion.setKeyValueAt(step / 4, core.QPointF(x, y))
            group.setLoopCount(-1 if activity in ("jump", "dance") else 1)
            group.start()

        class View(gui.QGraphicsView):
            def keyPressEvent(self, event):
                keys = {
                    core.Qt.Key_J: "jump",
                    core.Qt.Key_D: "dance",
                    core.Qt.Key_C: "rest",
                    core.Qt.Key_Escape: "rest",
                }
                if event.key() in keys:
                    choose(keys[event.key()])
                    event.accept()
                else:
                    gui.QGraphicsView.keyPressEvent(self, event)

        view = View(scene, handle.widget)
        layout.addWidget(view)
        layout.addWidget(
            gui.QLabel(
                "Drag a joint. J jumps, D dances, C rests; Escape returns to rest.",
                handle.widget,
            )
        )
        joints, bones, motions = [], [], []
        group = core.QParallelAnimationGroup(handle.widget)
        handle.cleanup.append(group.stop)
        for index, (x, y) in enumerate(keyframe("rest", 0)):
            marker = gui.QLabel()
            marker.setFixedSize(12, 12)
            marker.setStyleSheet("background: #d79c48; border-radius: 6px")
            proxy = embed(qt, scene, marker)
            proxy.setFlag(gui.QGraphicsItem.ItemIsMovable, True)
            proxy.setPos(x, y)
            joints.append(proxy)
            motion = core.QPropertyAnimation(proxy, core.QByteArray(b"pos"), group)
            motion.setDuration(1400)
            group.addAnimation(motion)
            motions.append(motion)
        for left, right in EDGES:
            line = gui.QGraphicsLineItem(core.QLineF(0, 0, 0, 0))
            line.setPen(gui.QPen(gui.QColor("#3d617c"), 3))
            scene.addItem(line)
            line.setZValue(-1)
            bones.append(line)
        lengths = [
            math.hypot(JOINTS[b][0] - JOINTS[a][0], JOINTS[b][1] - JOINTS[a][1])
            for a, b in EDGES
        ]

        def stabilize():
            for (left, right), bone, length in zip(EDGES, bones, lengths):
                a, b = value(joints[left], "pos"), value(joints[right], "pos")
                ax, ay, bx, by = (
                    value(a, "x"),
                    value(a, "y"),
                    value(b, "x"),
                    value(b, "y"),
                )
                dx, dy = bx - ax, by - ay
                distance = math.hypot(dx, dy)
                if distance < 0.001:
                    dx, dy, distance = length, 0, length
                bx, by = ax + dx * length / distance, ay + dy * length / distance
                joints[right].setPos(bx, by)
                bone.setLine(ax + 6, ay + 6, bx + 6, by + 6)

        flash = core.QTimer(handle.widget)
        flash.setSingleShot(True)
        wire(
            handle,
            flash,
            "timeout()",
            lambda *args: scene.setBackgroundBrush(gui.QBrush(gui.QColor("white"))),
        )
        handle.cleanup.append(flash.stop)
        lightning = gui.QGraphicsLineItem(core.QLineF(80, 0, 300, 230))
        lightning.setPen(gui.QPen(gui.QColor("#e3b91f"), 4))
        scene.addItem(lightning)
        lightning.hide()
        wire(handle, flash, "timeout()", lambda *args: lightning.hide())
        randomizer = random.Random()

        def strike():
            if state["activity"] != "dead" and randomizer.randrange(8) == 0:
                choose("dead")
                lightning.show()
                scene.setBackgroundBrush(gui.QBrush(gui.QColor("#fff4ac")))
                flash.start(120)

        frame_timer = timer(qt, handle, 25, stabilize)
        storm_timer = timer(qt, handle, 3000, strike)
        handle.controls.update(
            scene=scene,
            view=view,
            joints=joints,
            bones=bones,
            group=group,
            motions=motions,
            choose=choose,
            stabilize=stabilize,
            timer=frame_timer,
            storm=storm_timer,
            flash=flash,
        )
        handle.inspect_ui = lambda: {
            "activity": state["activity"],
            "joints": len(joints),
            "bones": len(bones),
        }
        stabilize()
        return handle
