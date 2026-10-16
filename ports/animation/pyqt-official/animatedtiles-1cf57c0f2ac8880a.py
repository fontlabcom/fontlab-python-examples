# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/1cf57c0f2ac8880a.md
# this_file: ports/animation/pyqt-official/animatedtiles-1cf57c0f2ac8880a.py

from contextlib import contextmanager

from fontlab_python_examples.handle import ExampleHandle


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


def button(qt, handle, layout, name, callback):
    item = qt.QtGui.QPushButton(name, handle.widget)
    layout.addWidget(item)
    handle.controls[name] = item
    wire(handle, item, "clicked()", lambda *args: callback())
    return item


import math
import random


def embed(qt, scene, widget):
    proxy = qt.QtGui.QGraphicsProxyWidget()
    proxy.setWidget(widget)
    scene.addItem(proxy)
    return proxy


def scene_view(qt, handle, layout):
    scene = qt.QtGui.QGraphicsScene(handle.widget)
    scene.setSceneRect(0, 0, 640, 420)
    view = qt.QtGui.QGraphicsView(scene, handle.widget)
    view.setRenderHint(qt.QtGui.QPainter.Antialiasing, True)
    layout.addWidget(view)
    handle.controls.update(scene=scene, view=view)
    return scene


def emblem(qt, color, index=0):
    pixmap = qt.QtGui.QPixmap(40, 40)
    pixmap.fill(qt.QtGui.QColor(color))
    painter = qt.QtGui.QPainter(pixmap)
    try:
        painter.setPen(qt.QtGui.QPen(qt.QtGui.QColor("white")))
        painter.drawEllipse(7 + index % 4, 7, 24, 24)
        painter.drawLine(8, 30, 30, 8 + index % 8)
    finally:
        painter.end()
    return pixmap


def animate_property(qt, handle, machine, obj, prop, duration=700, pause=0):
    motion = qt.QtCore.QPropertyAnimation(
        obj, qt.QtCore.QByteArray(prop.encode()), handle.widget
    )
    motion.setDuration(duration)
    motion.setEasingCurve(qt.QtCore.QEasingCurve(qt.QtCore.QEasingCurve.OutBack))
    group = qt.QtCore.QSequentialAnimationGroup(handle.widget)
    if pause:
        group.addPause(pause)
    group.addAnimation(motion)
    machine.addDefaultAnimation(group)
    handle.cleanup.append(group.stop)
    return motion


def positions(name):
    randomizer = random.Random(20261015)
    result = []
    for index in range(64):
        angle = 2 * math.pi * index / 64
        if name == "Grid":
            x, y = 112 + index % 8 * 46, 22 + index // 8 * 46
        elif name == "Ellipse":
            x, y = 300 + 260 * math.cos(angle), 190 + 160 * math.sin(angle)
        elif name == "Figure eight":
            x, y = 300 + 240 * math.sin(angle), 190 + 155 * math.sin(2 * angle)
        elif name == "Scatter":
            x, y = randomizer.randrange(590), randomizer.randrange(370)
        else:
            x, y = 300 + index % 4 * 2, 190 + index // 4 * 2
        result.append((x, y))
    return result


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Tile formations") as (handle, layout):
        scene = scene_view(qt, handle, layout)
        scene.setBackgroundBrush(gui.QBrush(emblem(qt, "#243947")))
        machine = core.QStateMachine(handle.widget)
        handle.cleanup.append(machine.stop)
        pictures = []
        for index in range(64):
            label = gui.QLabel()
            label.setPixmap(emblem(qt, "#437c94", index))
            proxy = embed(qt, scene, label)
            proxy.setGeometry(core.QRectF(300, 190, 40, 40))
            pictures.append(proxy)
            animate_property(
                qt, handle, machine, proxy, "geometry", 500 + index * 9, index * 5
            )
        names = ["Grid", "Ellipse", "Figure eight", "Scatter", "Center"]
        states, choices, selected = [], [], {"layout": "Grid"}
        for name in names:
            state = core.QState(machine)
            states.append(state)
            for item, (x, y) in zip(pictures, positions(name)):
                state.assignProperty(item, "geometry", core.QRectF(x, y, 40, 40))
            choice = button(qt, handle, layout, name, lambda: None)
            symbol = gui.QPixmap(48, 36)
            symbol.fill(gui.QColor("#f3f6ed"))
            painter = gui.QPainter(symbol)
            try:
                painter.setBrush(gui.QBrush(gui.QColor("#587c54")))
                for x, y in positions(name)[::4]:
                    painter.drawEllipse(core.QPointF(3 + x / 15, 3 + y / 15), 1.5, 1.5)
            finally:
                painter.end()
            choice.setIcon(gui.QIcon(symbol))
            choices.append(choice)
            wire(
                handle,
                state,
                "entered()",
                lambda *args, label=name: selected.update(layout=label),
            )
        for state in states:
            for choice, target in zip(choices, states):
                state.addTransition(choice, "2clicked(bool)", target)
        machine.setInitialState(states[0])
        machine.start()
        handle.controls.update(
            machine=machine, tiles=pictures, choices=choices, states=states
        )
        handle.inspect_ui = lambda: {
            "tiles": len(pictures),
            "layout": selected["layout"],
        }
        return handle
