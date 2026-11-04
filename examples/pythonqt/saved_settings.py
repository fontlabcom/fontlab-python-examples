# this_file: examples/pythonqt/saved_settings.py
# SPDX-License-Identifier: Apache-2.0
"""What: A form whose values survive closing the panel and restarting FontLab.
Shows: QSettings with an organisation/application namespace of its own, typed
defaults, explicit Save and Reset buttons, and checking QSettings.status() so a
failed write is reported instead of ignored.
Run: run from the Scripts menu. Edit the fields, press Save, close the panel,
run it again: the saved values return. Reset removes only this example's keys.
Setup: FontLab 9, Python 3.11, Fly with App (fly.ap.scripting). No font is
touched. The settings use their own namespace, never FontLab's preferences.

QSettings returns strings from some back ends, so the helpers convert every
value to the declared type and fall back to the default on bad data.
"""

from __future__ import annotations

from typing import Any

KEY = "pythonqt-example-saved-settings"
ORGANIZATION = "FontLab Python Examples"
APPLICATION = "Saved Settings"
DEFAULTS: dict[str, Any] = {"sample": "Hamburgefonstiv", "size": 48, "uppercase": False}
NO_ERROR = 0


def read(owner: Any, name: str) -> Any:
    """Qt properties may come back as values or as bound methods; accept both."""
    item = getattr(owner, name)
    return item() if callable(item) else item


def coerce(name: str, raw: Any) -> Any:
    """Convert a stored value to the type of its default; bad data gives the default."""
    default = DEFAULTS[name]
    try:
        if isinstance(default, bool):
            return raw if isinstance(raw, bool) else str(raw).lower() in {"true", "1"}
        return type(default)(raw)
    except (TypeError, ValueError):
        return default


def load(settings: Any) -> dict[str, Any]:
    return {name: coerce(name, settings.value(name, default)) for name, default in DEFAULTS.items()}


def save(settings: Any, values: dict[str, Any]) -> None:
    for name in DEFAULTS:
        settings.setValue(name, values[name])
    settings.sync()  # Flush now, then check that the store really accepted the write.
    status = settings.status()
    if getattr(status, "value", status) != NO_ERROR:
        raise OSError("The settings could not be saved.")


def reset(settings: Any) -> None:
    for name in DEFAULTS:
        settings.remove(name)
    settings.sync()


def build(parent: Any) -> Any:
    from fly import qt

    core, gui = qt.QtCore, qt.QtGui
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)
    panel.setWindowTitle("Saved Settings")
    panel.setAttribute(core.Qt.WA_DeleteOnClose)
    # Parenting the QSettings to the panel releases it with the panel.
    settings = core.QSettings(ORGANIZATION, APPLICATION, panel)
    saved = load(settings)
    sample = gui.QLineEdit(saved["sample"], panel)
    size = gui.QSpinBox(panel)
    size.setRange(6, 400)
    size.setValue(saved["size"])
    upper = gui.QCheckBox("Uppercase", panel)
    upper.setChecked(saved["uppercase"])
    note = gui.QLabel("", panel)
    form = gui.QFormLayout()
    form.addRow("Sample text", sample)
    form.addRow("Size", size)
    form.addRow("", upper)
    buttons = gui.QHBoxLayout()
    layout = gui.QVBoxLayout(panel)
    layout.addLayout(form)
    layout.addLayout(buttons)
    layout.addWidget(note)

    def current() -> dict[str, Any]:
        # Qt properties may come back as values or as bound methods; accept both.
        return {"sample": str(read(sample, "text")), "size": int(read(size, "value")),
                "uppercase": bool(read(upper, "checked"))}

    def do_save(*args: Any) -> None:
        try:
            save(settings, current())
            note.setText("Saved.")
        except Exception as error:  # noqa: BLE001 - Qt callback boundary
            note.setText(f"Not saved: {error}")

    def do_reset(*args: Any) -> None:
        reset(settings)
        sample.setText(DEFAULTS["sample"])
        size.setValue(DEFAULTS["size"])
        upper.setChecked(DEFAULTS["uppercase"])
        note.setText("Reset to defaults.")

    for text, call in (("Save", do_save), ("Reset", do_reset)):
        button = gui.QPushButton(text, panel)
        button.clicked.connect(call)
        buttons.addWidget(button)
    return panel


def main() -> Any:
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(build, KEY)


if __name__ == "__main__":
    main()
