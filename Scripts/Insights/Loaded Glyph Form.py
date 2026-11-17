# this_file: Scripts/Insights/Loaded Glyph Form.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (source grant unresolved; no code copied):
# _reference/RobotLocomotion_director/src/python/director/affordancepanel.py:39
"""Demonstrate loaded glyph form with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


UI = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- this_file: ports/insights/loaded-glyph-form.ui -->\n<!-- SPDX-License-Identifier: Apache-2.0; original owned form. -->\n<ui version="4.0">\n <class>GlyphMetricsForm</class>\n <widget class="QWidget" name="GlyphMetricsForm">\n  <layout class="QVBoxLayout" name="formLayout">\n   <item><widget class="QLineEdit" name="glyphName"><property name="text"><string>A</string></property></widget></item>\n   <item><widget class="QSpinBox" name="advanceBox"><property name="maximum"><number>2000</number></property><property name="value"><number>600</number></property></widget></item>\n   <item><widget class="QPushButton" name="applyButton"><property name="text"><string>Preview sample metrics</string></property></widget></item>\n   <item><widget class="QLabel" name="resultLabel"><property name="text"><string>A: advance 600</string></property></widget></item>\n  </layout>\n </widget>\n <resources/>\n <connections/>\n</ui>\n'


def _load(qt: Any, parent: Any) -> Any:
    from PythonQt import QtUiTools

    source = qt.QtCore.QBuffer()
    source.setData(qt.QtCore.QByteArray(UI.encode("utf-8")))
    loader = None
    try:
        loader = QtUiTools.QUiLoader()
        if not source.open(qt.QtCore.QIODevice.ReadOnly):
            raise OSError(f"Cannot open owned form: {source.errorString()}")
        form = loader.load(source, parent)
        if form is None:
            raise RuntimeError(f"Cannot load owned form: {loader.errorString()}")
        return form
    finally:
        source.close()
        source.deleteLater()
        if loader is not None:
            loader.deleteLater()


def build(qt: Any) -> ExampleHandle:
    with S.Session(qt, "Loaded sample glyph form", qt.QtGui.QWidget()) as session:
        handle = session.h
        form = _load(qt, handle.widget)
        qt.QtGui.QVBoxLayout(handle.widget).addWidget(form)
        names, pending = {}, [form]
        while pending:
            child = pending.pop()
            names[str(S.value(child, "objectName"))] = child
            pending.extend(child.children())
        needed = ("glyphName", "advanceBox", "applyButton", "resultLabel")
        if not all(name in names for name in needed):
            raise RuntimeError("Owned form is missing required named controls")
        glyph, advance, apply, result = [names[name] for name in needed]
        state = {"glyph_name": "A", "advance": 600}

        def preview() -> None:
            state.update(glyph_name=str(S.value(glyph, "text")), advance=int(S.value(advance, "value")))
            result.setText(f"{state['glyph_name']}: advance {state['advance']}")

        handle.connect_old(apply, "clicked()", preview)
        handle.controls.update(
            glyph_name=glyph, advance=advance, apply=apply, result=result, form=form
        )
        handle.inspect_ui = lambda: {**state, "result": str(S.value(result, "text"))}
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_loaded-glyph-form", "Loaded Glyph Form")


if __name__ == "__main__":
    main()
