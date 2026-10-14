# this_file: ports/designer-ui/pyqt-examples/main-402068f40005cd66.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann's pyqt/examples, src/05 Qt Designer Python/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for exact provenance.
"""Load the original Designer UI and its OK/Cancel connections via QUiLoader."""

from pathlib import Path
from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def _load(qt: Any) -> Any:
    path = Path(__file__).with_name("dialog-0bf07d6f0c55bc7e.ui")
    source = qt.QtCore.QFile(str(path))
    loader = None
    try:
        loader = qt.QtUiTools.QUiLoader()
        if not source.open(qt.QtCore.QIODevice.ReadOnly):
            raise OSError(
                f"Cannot open Designer UI: {path.name}: {source.errorString()}"
            )
        window = loader.load(source)
        if window is None:
            raise RuntimeError(f"Cannot load Designer UI: {loader.errorString()}")
        return window
    finally:
        source.close()
        source.deleteLater()
        if loader is not None:
            loader.deleteLater()


def build(qt: Any) -> ExampleHandle:
    window = _load(qt)
    handle = ExampleHandle(window, lambda: {"result": int(window.result())})
    try:
        window.setModal(False)
    except BaseException:
        handle.close()
        raise
    return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("402068f40005cd66")
