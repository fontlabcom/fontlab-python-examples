# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/bcfa5de0140286d5.md
# this_file: ports/designer/pyqt-official/pydemo-bcfa5de0140286d5.py

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
    with S.Session(qt, "Rich text component") as s:
        s.vertical()
        view = s.keep("text", s.g.QTextEdit(s.window))
        s.add(view)
        view.setReadOnly(True)
        view.setHtml(
            "<h1>A small reading room</h1><p><b>Bold</b> ideas and <i>quiet</i> details.</p><ul><li>One useful example</li><li>A second observation</li></ul>"
        )
        s.state.update(zoom=0, author="Example author", notifications=[])

        def zoom(n):
            n = max(-10, min(30, int(n)))
            delta = n - s.state["zoom"]
            view.zoomIn(delta)
            s.state["zoom"] = n
            s.state["notifications"].append(n)

        s.keep("set_zoom", zoom)
        s.keep("reset_zoom", lambda: zoom(0))
        s.keep("set_author", lambda text: s.state.update(author=str(text)))
        s.keep("reset_author", lambda: s.state.update(author="Example author"))
        return s.h
