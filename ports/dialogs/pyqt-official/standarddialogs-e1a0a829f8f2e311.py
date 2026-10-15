# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/e1a0a829f8f2e311.md
# this_file: ports/dialogs/pyqt-official/standarddialogs-e1a0a829f8f2e311.py

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
    with S.Session(qt, "Asynchronous standard dialogs", qt.QtGui.QDialog()) as s:
        s.vertical()
        s.check("native", "Prefer native files (host uses owned dialogs)")
        kinds = [
            "Integer",
            "Decimal",
            "Item",
            "Text",
            "Color",
            "Font",
            "Directory",
            "File",
            "Files",
            "Save",
            "Critical",
            "Information",
            "Question",
            "Warning",
            "Error",
        ]
        error = s.keep("error_dialog", s.alert(s.g.QErrorMessage(s.window)))

        def launch(kind, label):
            if kind == "Error":
                error.showMessage("Example message: review the sample settings.")
                return
            if kind in ["Directory", "File", "Files", "Save"]:
                dialog = s.choose(
                    lambda path: label.setText(path),
                    save=kind == "Save",
                    directory=kind == "Directory",
                )
                if kind == "Files":
                    dialog.setFileMode(s.g.QFileDialog.ExistingFiles)
                    s.link(
                        dialog,
                        "accepted()",
                        lambda *a: label.setText("; ".join(dialog.selectedFiles())),
                    )
                return
            if kind in ["Integer", "Decimal", "Item", "Text"]:
                dialog = s.g.QInputDialog(s.window)
                dialog.setLabelText("Choose a sample " + kind.lower())
                if kind == "Integer":
                    dialog.setInputMode(s.g.QInputDialog.IntInput)
                    dialog.setIntRange(-1000, 1000)
                elif kind == "Decimal":
                    dialog.setInputMode(s.g.QInputDialog.DoubleInput)
                    dialog.setDoubleRange(-1000.0, 1000.0)
                    dialog.setDoubleDecimals(3)
                elif kind == "Item":
                    dialog.setComboBoxItems(["Spring", "Summer", "Autumn", "Winter"])
                    dialog.setComboBoxEditable(False)
                accessor = {"Integer": "intValue", "Decimal": "doubleValue"}.get(
                    kind, "textValue"
                )
                read = lambda: str(S.value(dialog, accessor))
            elif kind == "Color":
                dialog = s.g.QColorDialog(s.window)
                read = lambda: str(dialog.selectedColor().name())
            elif kind == "Font":
                dialog = s.g.QFontDialog(s.window)
                read = lambda: str(dialog.selectedFont().family())
            else:
                dialog = s.g.QMessageBox(s.window)
                dialog.setText("Choose a response for " + kind.lower())
                dialog.setIcon(getattr(s.g.QMessageBox, kind))
                if kind == "Warning":
                    dialog.addButton("Save later", s.g.QMessageBox.AcceptRole)
                    dialog.addButton("Retry", s.g.QMessageBox.ActionRole)
                else:
                    dialog.setStandardButtons(
                        s.g.QMessageBox.Ok | s.g.QMessageBox.Cancel
                    )
                read = lambda: (
                    str(dialog.clickedButton().text)
                    if dialog.clickedButton() is not None
                    else ""
                )
            s.alert(dialog)
            s.keep("dialog_" + kind, dialog)
            s.link(dialog, "accepted()", lambda *a: label.setText(read()))
            if kind in ["Critical", "Information", "Question", "Warning"]:
                s.link(
                    dialog,
                    "buttonClicked(QAbstractButton*)",
                    lambda button: label.setText(str(S.value(button, "text"))),
                )
            dialog.open()

        for kind in kinds:
            row = s.g.QHBoxLayout()
            s.layout.addLayout(row)
            label = s.keep("result_" + kind, s.g.QLabel("", s.window))
            row.addWidget(label)
            button = s.g.QPushButton(kind, s.window)
            row.addWidget(button)
            s.keep(kind, button)
            s.link(button, "clicked()", lambda *a, k=kind, l=label: launch(k, l))
        return s.h
