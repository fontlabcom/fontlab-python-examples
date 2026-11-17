# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c1b878b63f80e733.md
# this_file: Scripts/Desktop/Tray Notifications.py

"""Tray Notifications: modeless PythonQt demonstration; no font data is changed."""

from fontlab_python_lessons import qt_demos as S



def pictogram(s, color="#347aab"):
    pixmap = s.g.QPixmap(48, 48)
    pixmap.fill(s.c.Qt.transparent)
    painter = s.g.QPainter(pixmap)
    try:
        painter.setBrush(s.g.QBrush(s.g.QColor(color)))
        painter.drawEllipse(4, 4, 40, 40)
    finally:
        painter.end()
    return pixmap

def build(qt):
    with S.Session(qt, "Explicit tray notifications", qt.QtGui.QDialog()) as s:
        s.vertical()
        choice = s.combo("icon", ["Blue marker", "Green marker", "Amber marker"])
        show = s.check("show", "Show tray icon")
        kind = s.combo("type", ["Information", "Warning", "Critical", "No icon"])
        duration = s.spin("duration", 5, 60, 10)
        title = s.line("title", "Example notification")
        body = s.line("body", "A manually requested sample message.")
        tray = s.keep("tray", s.g.QSystemTrayIcon(s.window))
        icons = [
            s.g.QIcon(pictogram(s, color))
            for color in ["#347aab", "#4e995c", "#d2a340"]
        ]
        tray.setIcon(icons[0])
        tray.hide()
        menu = s.g.QMenu(s.window)
        for text, fn in [
            ("Minimize", lambda: s.window.window().showMinimized()),
            ("Maximize", lambda: s.window.window().showMaximized()),
            ("Restore", lambda: s.window.window().showNormal()),
            ("Quit", s.h.close),
        ]:
            action = s.g.QAction(text, s.window)
            menu.addAction(action)
            s.link(action, "triggered()", lambda *a, cb=fn: cb())
        tray.setContextMenu(menu)
        s.keep("tray_menu", menu)
        s.link(show, "toggled(bool)", lambda flag: tray.setVisible(flag))
        s.link(
            choice, "currentIndexChanged(int)", lambda index: tray.setIcon(icons[index])
        )
        s.link(
            tray,
            "activated(QSystemTrayIcon::ActivationReason)",
            lambda reason: s.window.window().showNormal(),
        )

        def notify():
            if not bool(S.value(show, "checked")):
                s.state["error"] = "Enable the tray icon first"
                return
            icon = [
                s.g.QSystemTrayIcon.Information,
                s.g.QSystemTrayIcon.Warning,
                s.g.QSystemTrayIcon.Critical,
                s.g.QSystemTrayIcon.NoIcon,
            ][int(S.value(kind, "currentIndex"))]
            tray.showMessage(
                str(S.value(title, "text")),
                str(S.value(body, "text")),
                icon,
                int(S.value(duration, "value")) * 1000,
            )
            s.state["notifications"] = s.state.get("notifications", 0) + 1

        s.button("message", "Show Message", notify)
        s.h.cleanup.insert(0, lambda: tray.hide() if not s.h.owner.closed else None)
        s.button("quit", "Quit", s.h.close)
        s.state["notifications"] = 0
        return s.h


def main():
    """Open this example through the retained App dialog owner."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_systray-c1b878b63f80e733', 'Tray Notifications')


if __name__ == "__main__":
    main()
