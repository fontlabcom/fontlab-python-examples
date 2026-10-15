# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b7283d74afb78218.md
# this_file: ports/animation/pyqt-official/moveblocks-b7283d74afb78218.py

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


def timer(qt, handle, interval, callback):
    item = qt.QtCore.QTimer(handle.widget)
    wire(handle, item, "timeout()", lambda *args: callback())
    handle.cleanup.append(item.stop)
    item.start(interval)
    return item


import math


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


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Moving blocks") as (handle, layout):
        scene = scene_view(qt, handle, layout)
        machine = core.QStateMachine(handle.widget)
        handle.cleanup.append(machine.stop)
        blocks = []
        for color in ("#467f9e", "#cd894b", "#7b9e46", "#925fa7"):
            tile = gui.QLabel()
            tile.setStyleSheet("background-color: " + color)
            tile.setMinimumSize(1, 1)
            proxy = embed(qt, scene, tile)
            blocks.append(proxy)
            motion = animate_property(qt, handle, machine, proxy, "geometry", 900, 100)
            motion.setEasingCurve(core.QEasingCurve(core.QEasingCurve.OutElastic))
        states, state_data = [], {"state": 0}
        for number in range(7):
            state = core.QState(machine)
            states.append(state)
            for index, block in enumerate(blocks):
                angle = 2 * math.pi * (index / 4 + number / 7)
                width = 55 + (index + number) % 3 * 24
                height = 45 + (index * 2 + number) % 3 * 22
                state.assignProperty(
                    block,
                    "geometry",
                    core.QRectF(
                        280 + 200 * math.cos(angle),
                        180 + 130 * math.sin(angle),
                        width,
                        height,
                    ),
                )
            wire(
                handle,
                state,
                "entered()",
                lambda *args, n=number: state_data.update(state=n),
            )
        ticker = timer(qt, handle, 1250, lambda: None)
        # A coprime stride visits all seven states without repeating neighbors.
        for index, state in enumerate(states):
            state.addTransition(ticker, "2timeout()", states[(index + 3) % 7])
        machine.setInitialState(states[0])
        machine.start()
        handle.controls.update(
            machine=machine, timer=ticker, blocks=blocks, states=states
        )
        handle.inspect_ui = lambda: dict(state_data)
        return handle
