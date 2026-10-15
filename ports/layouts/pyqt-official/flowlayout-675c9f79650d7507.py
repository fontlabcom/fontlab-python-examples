# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/675c9f79650d7507.md
# this_file: ports/layouts/pyqt-official/flowlayout-675c9f79650d7507.py

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


def arrange(width, sizes, margin=10, spacing=8):
    x = y = margin
    row_height = 0
    rects = []
    for w, h in sizes:
        if x > margin and x + w > max(margin, width - margin):
            x = margin
            y += row_height + spacing
            row_height = 0
        rects.append((x, y, w, h))
        x += w + spacing
        row_height = max(row_height, h)
    return rects, y + row_height + margin


def build(qt):
    with S.Session(qt, "Wrapping buttons") as s:
        buttons = []

        reflow_callback = [lambda: None]

        class Flow(qt.QtGui.QWidget):
            def resizeEvent(self, event):
                qt.QtGui.QWidget.resizeEvent(self, event)
                reflow_callback[0]()

        area = s.keep("flow", Flow(s.window))
        root = s.vertical()
        root.addWidget(area)
        for text in ["One", "A longer choice", "Small", "A very wide button", "Done"]:
            buttons.append(s.g.QPushButton(text, area))

        # Reflow against the actual content width, without native layout subclassing.
        def reflow(*args):
            sizes = [
                (
                    int(S.value(S.value(b, "sizeHint"), "width")),
                    int(S.value(S.value(b, "sizeHint"), "height")),
                )
                for b in buttons
            ]
            rects, height = arrange(int(S.value(area, "width")), sizes)
            for b, rect in zip(buttons, rects):
                b.setGeometry(*rect)
            area.setMinimumHeight(height)
            s.state["rows"] = len({r[1] for r in rects})

        reflow_callback[0] = reflow
        reflow()
        s.keep("reflow", reflow)
        return s.h
