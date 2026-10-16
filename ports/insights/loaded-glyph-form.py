# this_file: ports/insights/loaded-glyph-form.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (source grant unresolved; no code copied):
# _reference/RobotLocomotion_director/src/python/director/affordancepanel.py:39
from pathlib import Path
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned, required


def _load(qt: Any, parent: Any) -> Any:
    loader_type = required(qt, "QtUiTools.QUiLoader")
    path = Path(__file__).with_suffix(".ui")
    source, loader = qt.QtCore.QFile(str(path)), None
    try:
        loader = loader_type()
        if not source.open(qt.QtCore.QIODevice.ReadOnly):
            raise OSError(f"Cannot open owned form {path.name}: {source.errorString()}")
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
    with owned(qt.QtGui.QWidget(), "Loaded sample glyph form") as handle:
        form = _load(qt, handle.widget)
        qt.QtGui.QVBoxLayout(handle.widget).addWidget(form)
        names, pending = {}, [form]
        while pending:
            child = pending.pop()
            names[str(child.objectName)] = child
            pending.extend(child.children())
        needed = ("glyphName", "advanceBox", "applyButton", "resultLabel")
        if not all(name in names for name in needed):
            raise RuntimeError("Owned form is missing required named controls")
        glyph, advance, apply, result = [names[name] for name in needed]
        state = {"glyph_name": "A", "advance": 600}

        def preview() -> None:
            state.update(glyph_name=str(glyph.text), advance=int(advance.value))
            result.setText(f"{state['glyph_name']}: advance {state['advance']}")

        handle.connect_old(apply, "clicked()", preview)
        handle.controls.update(
            glyph_name=glyph, advance=advance, apply=apply, result=result, form=form
        )
        handle.inspect_ui = lambda: {**state, "result": str(result.text)}
        return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("loaded-glyph-form")
