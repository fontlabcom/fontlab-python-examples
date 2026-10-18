# this_file: lessons/src/fontlab_python_lessons/forms.py
# SPDX-License-Identifier: Apache-2.0
"""Load only the packaged owned Designer form, with bounded known controls.

The resource is packaged beside this module. QFile and QUiLoader are always
released. Do not accept arbitrary form paths or enumerate native widget lists.
"""
from importlib.resources import as_file, files
from typing import Any

CONTROL_NAMES = ("glyphName", "actualAdvance", "actualLsb", "advanceBox",
                 "previewButton", "resultLabel")
CONTROL_TYPES = ("QComboBox", "QLabel", "QLabel", "QDoubleSpinBox", "QPushButton", "QLabel")


def load_form(qt: Any, parent: Any) -> tuple[Any, dict[str, Any]]:
    """Read the installed .ui and verify all required controls before use.

    Known object names are queried individually. The form belongs to parent;
    load/validation errors delete any partially returned form before raising.
    """
    resource = files(__package__).joinpath("resources/glyph-metrics-form.ui")
    with as_file(resource) as path:
        source = qt.QtCore.QFile(str(path))
        loader, form = None, None
        try:
            loader = qt.QtUiTools.QUiLoader()
            if not source.open(qt.QtCore.QIODevice.ReadOnly):
                raise OSError("Cannot open the packaged glyph metrics form.")
            form = loader.load(source, parent)
            if form is None:
                raise ValueError("Cannot load glyph metrics form: " + loader.errorString())
            controls = {name: form.findChild(qt.QtGui.QWidget, name)
                        for name in CONTROL_NAMES}
            if any(value is None for value in controls.values()):
                raise ValueError("The glyph metrics form lacks required controls.")
            if any(not controls[name].inherits(class_name)
                   for name, class_name in zip(CONTROL_NAMES, CONTROL_TYPES, strict=True)):
                raise ValueError("The glyph metrics form has a wrong control type.")
            return form, controls
        except Exception:
            if form is not None:
                form.close()
                form.deleteLater()
            raise
        finally:
            source.close()
            source.deleteLater()
            if loader is not None:
                loader.deleteLater()
