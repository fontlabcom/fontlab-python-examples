# this_file: Scripts/Tools/FontLab Qt Slot Reference.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source: rescued/part2/ports/insights/compiled-slot-exposure.py
# preserved-source-sha256: e81955446fce469142051973c7c630cac6d44b88aa46ee1ea5aa8cd5e8805108
"""Read live FontLab widget signals and slots for a scripting reference.

What: Select the main window, the focused widget captured when this panel opens,
or a widget from the main window's direct children. List signals and slots with
signatures, plus fixed PythonQt rules for safe callback wiring.
How: Use direct native accessors. Disable Python GC while converting the one
children list; do not traverse the widget tree or read arbitrary property values.
Read only Qt metadata. If method enumeration is absent, report that limitation
and keep the PythonQt rules visible. No discovered method is invoked.
Why: Inspect the compiled interface before writing a FontLab callback.
Usage: Focus the target widget before running this script. Choose an object,
then Read Reference and copy the JSON. Run again to refresh the object choices.
Destroyed targets are refused. No document is needed and no font is changed.
Benefit: Keep exact signal/slot signatures beside practical PythonQt rules.
A Qt declaration does not prove PythonQt can call every listed overload.
Setup: FontLab 9, Python 3.11, Fly and App draft_signals/qt_properties.
Independent rewrite of compiled-slot-exposure.
Based on the author's own FontLab sample, Apache-2.0.
No original source body is redistributed.
"""

import gc
import json
from typing import Any

TITLE = "FontLab Qt Slot Reference"
HELP = "Choose a live widget. Read signals, slots and PythonQt rules; copy JSON with Cmd+C."


PYTHONQT_RULES = (
    "Widgets live in PythonQt.QtGui; PythonQt has no QtWidgets module.",
    "Signals pass all their arguments to native slots. Wrap the native slot in a lambda that accepts those arguments.",
    "In the ported calculator, sender() was observed to return None in PythonQt slots. Bind the emitting widget explicitly.",
    "QProcess.finished.connect binds the deprecated finished(int) overload.",
    "PythonQt enum arguments required explicit value classes for setEasingCurve, for example QEasingCurve(QEasingCurve.OutElastic), and for QDialogButtonBox flags; plain integer flags selected its Orientation overload.",
    "Never apply unary minus to a Qt wrapper. Negate its numeric components instead.",
    "Disconnect every signal the script connected before deleteLater or close; deleting a widget with children still holding Python slot targets crashed FontLab.",
    "Direct native-slot and Python bound-method connections on the same receiver can crash FontLab during disconnect. Wrap native slots in lambdas.",
    "Read QByteArray payloads with data(); bytes(wrapper) raises in PythonQt.",
)


def object_choices(gui: Any, owner: Any) -> list[tuple[str, Any]]:
    """Capture direct targets with GC paused during native-list conversion only."""
    if owner is None:
        raise ValueError("FontLab's main window is required.")
    targets = [("Main window", owner), ("Focused widget at panel open", gui.QApplication.focusWidget())]
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        for index, child in enumerate(owner.children()):
            if child.isWidgetType():
                label = f"Direct child {index}: {child.metaObject().className()}"
                targets.append((label, child))
    finally:
        if was_enabled:
            gc.enable()
    return targets


def slot_report(owner: Any, method_kinds: Any) -> str:
    """Read only declared signals/slots; give a usable fallback on older bindings."""
    if owner is None:
        raise ValueError("The selected widget is absent or destroyed. Run the tool again.")
    result = {"class": "", "signals": [], "slots": [], "invoked": False,
              "availability": "available", "PythonQt rules": PYTHONQT_RULES}
    try:
        meta = owner.metaObject()
        result["class"] = str(meta.className())
        groups = {method_kinds.Signal: "signals", method_kinds.Slot: "slots"}
        for index in range(meta.methodCount()):
            method = meta.method(index)
            group = groups.get(method.methodType())
            if group is not None:
                payload = method.methodSignature().data()
                signature = payload.decode("utf-8") if isinstance(payload, bytes) else str(payload)
                result[group].append(signature)
        for group in ("signals", "slots"):
            result[group] = sorted(set(result[group]))
    except (AttributeError, TypeError, RuntimeError, ValueError) as error:
        result.update(signals=[], slots=[], availability="not available on this build",
                      detail=f"{type(error).__name__}: {error}")
    return json.dumps(result, ensure_ascii=True, indent=2)


_PANELS: list[Any] = []


def show(qt: Any, parent: Any) -> Any:
    """Open an owned tool window; use App to fence and disconnect callbacks."""
    import fly.ap.draft_signals as signals

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Keep controls and callback references until native cleanup succeeds."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(700, 500)
            self.box = gui.QVBoxLayout(self)
            self.box.setContentsMargins(16, 16, 16, 16)
            self.box.setSpacing(8)
            self.status_line = gui.QLabel(HELP, self)
            self.status_line.setWordWrap(True)
            self.box.addWidget(self.status_line)
            self.scope = signals.Scope(lambda error: self.status_line.setText(str(error)))
            self.scope.connect(self.destroyed, lambda *args: self.release_owner())

        def add_button(self, text: str, action: Any) -> None:
            """Wrap signal arguments; never connect a native slot directly."""
            button = gui.QPushButton(text, self)
            self.box.addWidget(button)
            self.scope.connect(button.clicked, lambda *args: action())

        def release_owner(self) -> None:
            """Drop Python references when FontLab destroys the native parent."""
            self.scope.finish(destroyed=True)
            self.targets = []
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Stop owned work and disconnect before scheduling native deletion."""
            self.stop_owned()
            if not self.scope.finish():
                event.ignore()
                return
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

        def stop_owned(self) -> None:
            """There is no queued work in this panel."""

        def forget_target(self, index: int) -> None:
            """Clear a destroyed native pointer without calling any of its members."""
            self.targets[index] = None

        def read_slots(self) -> None:
            """Read the selected target; missing metadata leaves the rules visible."""
            import fly.ap.qt_properties as properties

            self.output_box.setPlainText(json.dumps({"PythonQt rules": PYTHONQT_RULES}, indent=2))
            index = int(properties.value(self.target_picker, "currentIndex"))
            if not 0 <= index < len(self.targets):
                raise ValueError("Choose an available widget.")
            report = slot_report(self.targets[index], getattr(core, "QMetaMethod", None))
            self.output_box.setPlainText(report)
            self.status_line.setText(json.loads(report)["availability"])

    choices = object_choices(gui, parent)
    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.targets = [target for _, target in choices]
        panel.target_picker = gui.QComboBox(panel)
        for index, (label, target) in enumerate(choices):
            panel.target_picker.addItem(label)
            if target is not None:
                panel.scope.connect(target.destroyed, lambda *args, index=index: panel.forget_target(index))
        panel.box.addWidget(panel.target_picker)
        panel.output_box = gui.QPlainTextEdit(panel)
        panel.output_box.setReadOnly(True)
        panel.box.addWidget(panel.output_box)
        panel.add_button("Read Reference", panel.read_slots)
        panel.output_box.setPlainText(json.dumps({"PythonQt rules": PYTHONQT_RULES}, indent=2))
        panel.show()
    except Exception:
        panel.stop_owned()
        if panel.scope.finish():
            _PANELS.remove(panel)
            panel.deleteLater()
        else:
            panel.show()
        raise
    return panel


def main() -> None:
    """Resolve the running FontLab window lazily; never create an application."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError, AttributeError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
