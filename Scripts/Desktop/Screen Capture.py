# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/65d15d1fbc1b15e9.md
# this_file: Scripts/Desktop/Screen Capture.py

"""Screen Capture: modeless PythonQt demonstration; no font data is changed."""

from pathlib import Path
from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Explicit screen capture") as s:
        s.vertical()
        preview = s.keep("preview", s.label("No screen captured"))
        delay = s.spin("delay", 0, 60, 0)
        hide = s.check("hide", "Hide this window during capture")
        image = [None]
        s.state.update(pending=False, captured=False)

        def capture():
            timer.stop()
            try:
                screens = list(s.g.QApplication.instance().screens())
                if screens:
                    image[0] = screens[0].grabWindow(0, 0, 0, -1, -1)
                    preview.setPixmap(
                        image[0].scaled(
                            S.value(preview, "size"),
                            s.c.Qt.KeepAspectRatio,
                            s.c.Qt.SmoothTransformation,
                        )
                    )
                    s.state["captured"] = True
            finally:
                s.window.window().show()
                delay.setEnabled(True)
                hide.setEnabled(True)
                new.setEnabled(True)
                s.state["pending"] = False

        timer = s.timer("capture_timer", 0, capture, single=True, start=False)

        def schedule():
            if s.state["pending"]:
                return
            s.state["pending"] = True
            delay.setEnabled(False)
            hide.setEnabled(False)
            new.setEnabled(False)
            if bool(S.value(hide, "checked")):
                s.window.window().hide()
            timer.start(int(S.value(delay, "value")) * 1000)

        def save(path):
            if image[0] is None:
                return
            target = Path(path).resolve()
            root = s.temp().resolve()
            if not target.is_relative_to(root):
                raise ValueError(
                    "Save the capture inside this example temporary folder"
                )
            if not image[0].save(str(target)):
                raise OSError("Cannot save capture")

        new = s.button("new", "New", schedule)
        s.button("save", "Save", lambda: s.choose(save, save=True))
        s.button("quit", "Quit", s.h.close)
        s.keep("capture", capture)
        s.keep("save_image", save)
        return s.h


def main():
    """Open this example through the retained App dialog owner."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_screenshot-65d15d1fbc1b15e9', 'Screen Capture')


if __name__ == "__main__":
    main()
