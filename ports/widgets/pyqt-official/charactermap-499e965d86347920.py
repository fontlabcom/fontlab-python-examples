# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/499e965d86347920.md
# this_file: ports/widgets/pyqt-official/charactermap-499e965d86347920.py

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

import unicodedata


def codepoint_at(x, y, cell):
    if cell <= 0 or x < 0 or y < 0:
        return None
    value = int(y) // cell * 16 + int(x) // cell
    return value if 0 <= int(x) // cell < 16 and 0 <= value < 65536 else None


def build(qt):
    with S.Session(qt, "Unicode BMP character grid") as s:
        s.vertical()
        family = s.keep("family", s.g.QFontComboBox(s.window))
        s.add(family)
        style = s.combo("style", ["Regular", "Bold", "Italic"])
        size = s.spin("size", 6, 72, 14)
        merge = s.check("merge", "Font merging", True)
        selected = s.line("selected")
        cell = [32]
        font = [s.g.QFont()]

        def text_at(point):
            return codepoint_at(
                int(S.value(point, "x")), int(S.value(point, "y")), cell[0]
            )

        class Grid(s.g.QWidget):
            def paintEvent(self, event):
                p = s.g.QPainter(self)
                try:
                    p.setFont(font[0])
                    rect = event.rect()
                    top = max(0, int(S.value(rect, "top")) // cell[0])
                    bottom = min(4095, int(S.value(rect, "bottom")) // cell[0])
                    for row in range(top, bottom + 1):
                        for col in range(16):
                            code = row * 16 + col
                            x = col * cell[0]
                            y = row * cell[0]
                            p.setPen(s.g.QColor("#c7ccd3"))
                            p.drawRect(x, y, cell[0], cell[0])
                            p.setPen(s.g.QColor("#253746"))
                            if unicodedata.category(chr(code)) not in ["Cn", "Cs"]:
                                p.drawText(
                                    x,
                                    y,
                                    cell[0],
                                    cell[0],
                                    s.c.Qt.AlignCenter,
                                    chr(code),
                                )
                finally:
                    p.end()

            def mousePressEvent(self, event):
                code = text_at(event.pos())
                if code is not None and unicodedata.category(chr(code)) not in [
                    "Cn",
                    "Cs",
                ]:
                    metrics = s.g.QFontMetrics(font[0])
                    if metrics.inFontUcs4(code):
                        selected.setText(str(S.value(selected, "text")) + chr(code))
                        s.state["last_codepoint"] = code

            def mouseMoveEvent(self, event):
                code = text_at(event.pos())
                if code is not None:
                    s.g.QToolTip.showText(
                        event.globalPos(),
                        f"U+{code:04X} " + unicodedata.name(chr(code), "Unassigned"),
                        self,
                    )

        grid = s.keep("grid", Grid(s.window))
        grid.setMouseTracking(True)
        scroll = s.keep("scroll", s.g.QScrollArea(s.window))
        scroll.setWidget(grid)
        s.add(scroll)

        def typography(*args):
            f = s.g.QFont(S.value(family, "currentFont"))
            f.setPointSize(int(S.value(size, "value")))
            f.setBold(int(S.value(style, "currentIndex")) == 1)
            f.setItalic(int(S.value(style, "currentIndex")) == 2)
            f.setStyleStrategy(
                s.g.QFont.PreferDefault
                if bool(S.value(merge, "checked"))
                else s.g.QFont.NoFontMerging
            )
            font[0] = f
            cell[0] = max(20, int(S.value(size, "value")) * 2 + 8)
            grid.setFixedSize(cell[0] * 16, cell[0] * 4096)
            grid.update()
            s.state["cell_size"] = cell[0]

        for obj, signal in [
            (family, "currentFontChanged(QFont)"),
            (style, "currentIndexChanged(int)"),
            (size, "valueChanged(int)"),
            (merge, "toggled(bool)"),
        ]:
            s.link(obj, signal, typography)
        s.button(
            "copy",
            "Copy selected text",
            lambda: s.g.QApplication.clipboard().setText(
                str(S.value(selected, "text"))
            ),
        )
        typography()
        return s.h
