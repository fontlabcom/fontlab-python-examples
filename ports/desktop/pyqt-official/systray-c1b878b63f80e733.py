# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c1b878b63f80e733.md
# this_file: ports/desktop/pyqt-official/systray-c1b878b63f80e733.py

import importlib.util
import sys
from pathlib import Path

_key = "fontlab_cleanroom_a_primitives"
if _key not in sys.modules:
    _path = (
        Path(__file__).resolve().parents[2]
        / "layouts/pyqt-official/basiclayouts-2f94fe07de765888.py"
    )
    _spec = importlib.util.spec_from_file_location(_key, _path)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_key] = _module
    try:
        _spec.loader.exec_module(_module)
    except BaseException:
        sys.modules.pop(_key, None)
        raise
S = sys.modules[_key]


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
            s.g.QIcon(S.pictogram(s, color))
            for color in ["#347aab", "#4e995c", "#d2a340"]
        ]
        tray.setIcon(icons[0])
        tray.hide()
        menu = s.g.QMenu(s.window)
        for text, fn in [
            ("Minimize", s.window.showMinimized),
            ("Maximize", s.window.showMaximized),
            ("Restore", s.window.showNormal),
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
            lambda reason: s.window.showNormal(),
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
