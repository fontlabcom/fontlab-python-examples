# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/9e21c6536fda7a23.md
# this_file: ports/widgets/pyqt-official/styles-9e21c6536fda7a23.py

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
    with S.Session(qt, "Local style gallery") as s:
        s.vertical()
        choice = s.combo("style", list(s.g.QStyleFactory.keys()))
        palette = s.check("palette", "Use style palette")
        disable = s.check("disable", "Disable samples")
        sample = s.keep("sample", s.g.QWidget(s.window))
        layout = s.vertical(sample)
        s.add(sample)
        for title in ["Choice group", "Action group"]:
            group = s.g.QGroupBox(title, sample)
            gl = s.vertical(group)
            layout.addWidget(group)
            if title == "Choice group":
                for label in ["First", "Second"]:
                    gl.addWidget(s.g.QRadioButton(label, group))
                gl.addWidget(s.g.QCheckBox("Independent", group))
            else:
                gl.addWidget(s.g.QPushButton("Sample action", group))
                s.spin("number", -20, 100, 10, gl)
        tabs = s.g.QTabWidget(sample)
        layout.addWidget(tabs)
        tabs.addTab(
            s.g.QTextEdit("New sample prose for a local style preview.", tabs), "Text"
        )
        table = s.g.QTableWidget(3, 2, tabs)
        tabs.addTab(table, "Table")
        progress = s.keep("progress", s.g.QProgressBar(sample))
        progress.setRange(0, 10000)
        progress.setValue(0)
        layout.addWidget(progress)

        def tick():
            n = int(S.value(progress, "value"))
            n = min(10000, n + max(1, (10000 - n) // 100))
            progress.setValue(n)
            s.state["progress"] = n
            if n == 10000:
                timer.stop()

        def style(*args):
            s.local_style(str(S.value(choice, "currentText")), [sample])
            if bool(S.value(palette, "checked")):
                sample.setPalette(sample.style().standardPalette())
            else:
                sample.setPalette(s.g.QPalette())

        s.link(choice, "currentIndexChanged(int)", style)
        s.link(palette, "toggled(bool)", style)
        s.link(disable, "toggled(bool)", sample.setDisabled)
        timer = s.timer("progress_timer", 30, tick)
        return s.h
