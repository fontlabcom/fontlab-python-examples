# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/29f6a7d0a3bb6813.md
# this_file: ports/animation/pyqt-official/states-29f6a7d0a3bb6813.py

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
    with owned(qt, "Scene states") as (handle, layout):
        scene = scene_view(qt, handle, layout)
        editor = gui.QTextEdit()
        editor.setPlainText("A small editor travelling through three arrangements.")
        edit_proxy = embed(qt, scene, editor)
        options = gui.QWidget()
        choices = gui.QVBoxLayout(options)
        for word in ("Draft", "Review", "Publish"):
            choices.addWidget(gui.QRadioButton(word, options))
        options_proxy = embed(qt, scene, options)
        cycle = gui.QPushButton("Arrange right")
        cycle_proxy = embed(qt, scene, cycle)
        cycle_proxy.setGeometry(core.QRectF(460, 360, 150, 40))
        icons = []
        for index in range(6):
            label = gui.QLabel()
            label.setPixmap(
                emblem(qt, ["#477994", "#8a6353", "#6c8c4d"][index % 3], index)
            )
            icons.append(embed(qt, scene, label))
        machine = core.QStateMachine(handle.widget)
        handle.cleanup.append(machine.stop)
        states, status = [], {"state": 0}
        for number in range(3):
            state = core.QState(machine)
            states.append(state)
            state.assignProperty(
                cycle,
                "text",
                ("Arrange right", "Arrange columns", "Arrange above")[number],
            )
            edit_geometry = (
                (20, 10, 590, 180),
                (270, 120, 350, 210),
                (200, 10, 420, 190),
            )[number]
            state.assignProperty(edit_proxy, "geometry", core.QRectF(*edit_geometry))
            state.assignProperty(
                options_proxy,
                "geometry",
                core.QRectF(20 if number == 1 else 260, 220, 180, 110),
            )
            state.assignProperty(options_proxy, "opacity", 0.0 if number == 0 else 1.0)
            for index, icon in enumerate(icons):
                x = 40 + index * 90 if number != 2 else 25 + index % 2 * 70
                y = 250 if number == 0 else 30 if number == 1 else 30 + index // 2 * 100
                state.assignProperty(icon, "geometry", core.QRectF(x, y, 40, 40))
                state.assignProperty(
                    icon,
                    "opacity",
                    1.0 if number == 2 or (index < 3) == (number == 0) else 0.0,
                )
                state.assignProperty(icon, "rotation", number * 25.0)
            wire(
                handle,
                state,
                "entered()",
                lambda *args, n=number: status.update(state=n),
            )
        for index, state in enumerate(states):
            state.addTransition(cycle, "2clicked(bool)", states[(index + 1) % 3])
        for proxy in [edit_proxy, options_proxy, *icons]:
            for prop in ("geometry", "opacity", "rotation"):
                animate_property(qt, handle, machine, proxy, prop)
        machine.setInitialState(states[0])
        machine.start()
        handle.controls.update(
            machine=machine, editor=editor, cycle=cycle, states=states, icons=icons
        )
        handle.inspect_ui = lambda: dict(status)
        return handle
