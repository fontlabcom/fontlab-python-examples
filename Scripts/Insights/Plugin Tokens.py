# this_file: Scripts/Insights/Plugin Tokens.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (source grant unresolved; no code copied):
# _reference/exp111_pyTSon-Scripts/include/pluginhost.py:420
"""Demonstrate plugin tokens with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with S.Session(qt, "Owned menu plug-in registry", gui.QMainWindow()) as session:
        handle = session.h
        window = handle.widget
        panel = gui.QWidget(window)
        window.setCentralWidget(panel)
        install_button = gui.QPushButton("Install sample plug-in", panel)
        unload_button = gui.QPushButton("Unload sample plug-in", panel)
        label = gui.QLabel("Unloaded", panel)
        layout = gui.QVBoxLayout(panel)
        for control in (install_button, unload_button, label):
            layout.addWidget(control)
        tokens, state, connection = {}, {"invocations": 0}, [None]

        def invoke(*_args: Any) -> None:
            state["invocations"] += 1
            label.setText(f"Sample action invoked {state['invocations']} times")

        def install() -> None:
            if tokens:
                return
            menu = window.menuBar().addMenu("Sample plug-in")
            tokens["proof-menu"] = menu
            action = gui.QAction("Preview sample advance", menu)
            tokens["advance-action"] = action
            signal = action.triggered
            handle.connect(signal, invoke)
            connection[0] = signal
            menu.addAction(action)
            handle.controls["plugin_action"] = action
            label.setText("Installed one menu/action token pair")

        def unload() -> None:
            if not tokens:
                return
            menu, action = tokens["proof-menu"], tokens.get("advance-action")
            if connection[0] is not None:
                handle.disconnect(connection[0], invoke)
                connection[0] = None
            if not handle.owner.closed:
                if action is not None:
                    menu.removeAction(action)
                window.menuBar().removeAction(menu.menuAction())
                label.setText("Unloaded")
            tokens.clear()
            handle.controls["plugin_action"] = None
            if not handle.owner.closed:
                menu.deleteLater()  # Menu owns its action; never delete the action twice.

        handle.cleanup.append(unload)
        handle.connect_old(install_button, "clicked()", install)
        handle.connect_old(unload_button, "clicked()", unload)
        handle.controls.update(
            install=install_button,
            unload=unload_button,
            plugin_action=None,
            status=label,
        )
        handle.inspect_ui = lambda: {
            **state,
            "tokens": sorted(tokens),
            "registered": bool(tokens),
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_plugin-tokens", "Plugin Tokens")


if __name__ == "__main__":
    main()
