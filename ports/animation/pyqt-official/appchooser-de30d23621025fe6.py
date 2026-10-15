# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/de30d23621025fe6.md
# this_file: ports/animation/pyqt-official/appchooser-de30d23621025fe6.py

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


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Application selector") as (handle, layout):
        scene = scene_view(qt, handle, layout)
        machine = core.QStateMachine(handle.widget)
        machine.setGlobalRestorePolicy(core.QState.RestoreProperties)
        handle.cleanup.append(machine.stop)
        initial = core.QState(machine)
        states, buttons, proxies = [], [], []
        selected = {"index": -1}
        colors = ["#4e7fa1", "#a16f4e", "#6c914e", "#8b63a1"]
        for index, (x, y) in enumerate(((20, 20), (500, 20), (20, 300), (500, 300))):
            item = gui.QPushButton(["Draw", "Read", "Listen", "Explore"][index])
            item.setIcon(gui.QIcon(emblem(qt, colors[index], index)))
            proxy = embed(qt, scene, item)
            proxy.setGeometry(core.QRectF(x, y, 110, 80))
            target = core.QState(machine)
            target.assignProperty(proxy, "geometry", core.QRectF(210, 120, 220, 160))
            states.append(target)
            buttons.append(item)
            proxies.append(proxy)
            animate_property(qt, handle, machine, proxy, "geometry")
            wire(
                handle,
                target,
                "entered()",
                lambda *args, i=index: selected.update(index=i),
            )
        for source in [initial, *states]:
            for item, target in zip(buttons, states):
                source.addTransition(item, "2clicked(bool)", target)
        machine.setInitialState(initial)
        machine.start()
        handle.controls.update(
            machine=machine, choices=buttons, pictures=proxies, states=states
        )
        handle.inspect_ui = lambda: dict(selected)
        return handle
