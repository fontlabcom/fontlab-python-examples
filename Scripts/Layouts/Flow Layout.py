# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/675c9f79650d7507.md
# this_file: Scripts/Layouts/Flow Layout.py

"""Show flow layout using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


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


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_flowlayout-675c9f79650d7507', 'Flow Layout')


if __name__ == "__main__":
    main()
