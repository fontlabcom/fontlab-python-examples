# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/a3b3cbe51c1506c6.md
# this_file: Scripts/Widgets/Animated Checker Player.py

"""Show animated checker player using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S

import struct


def animation():
    data = bytearray(
        b"GIF89a"
        + struct.pack("<HHBBB", 16, 16, 128, 0, 0)
        + bytes([40, 115, 180, 230, 170, 55])
    )
    data.extend(b"!\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00")
    for frame in range(2):
        data.extend(
            b"!\xf9\x04\x00"
            + struct.pack("<H", 30)
            + b"\x00\x00,\x00\x00\x00\x00"
            + struct.pack("<HH", 16, 16)
            + b"\x00\x02"
        )
        # Clear before every pixel keeps the freshly authored LZW stream at 3 bits.
        codes = []
        for y in range(16):
            for x in range(16):
                codes.extend([4, (x // 4 + y // 4 + frame) % 2])
        codes.append(5)
        bits = 0
        count = 0
        payload = bytearray()
        for code in codes:
            bits |= code << count
            count += 3
            while count >= 8:
                payload.append(bits & 255)
                bits >>= 8
                count -= 8
        if count:
            payload.append(bits & 255)
        for offset in range(0, len(payload), 255):
            block = payload[offset : offset + 255]
            data.append(len(block))
            data.extend(block)
        data.append(0)
    return bytes(data + b";")


def build(qt):
    with S.Session(qt, "Animated checker player") as s:
        s.vertical()
        preview = s.keep("preview", s.label(""))
        movie = s.keep("movie", s.g.QMovie(s.window))
        preview.setMovie(movie)
        slider = s.keep("frame", s.g.QSlider(s.c.Qt.Horizontal, s.window))
        s.add(slider)
        speed = s.spin("speed", 1, 500, 100)
        fit = s.check("fit", "Fit preview")
        busy = [False]

        def refresh(*args):
            busy[0] = True
            try:
                slider.setRange(0, max(0, int(S.value(movie, "frameCount")) - 1))
                slider.setValue(max(0, int(S.value(movie, "currentFrameNumber"))))
                s.state["frame"] = int(S.value(movie, "currentFrameNumber"))
                s.state["movie_state"] = int(S.value(movie, "state"))
            finally:
                busy[0] = False

        def load(path):
            movie.stop()
            movie.setFileName(path)
            if not movie.isValid():
                s.state["error"] = "This file is not a supported animation"
                return False
            movie.jumpToFrame(0)
            refresh()
            s.state["error"] = ""
            return True

        path = s.temp() / "checker.gif"
        path.write_bytes(animation())
        load(str(path))
        s.link(movie, "frameChanged(int)", refresh)
        s.link(movie, "stateChanged(QMovie::MovieState)", refresh)
        s.link(
            slider,
            "valueChanged(int)",
            lambda n: movie.jumpToFrame(n) if not busy[0] else None,
        )
        s.link(speed, "valueChanged(int)", movie.setSpeed)
        s.link(fit, "toggled(bool)", lambda enabled: preview.setScaledContents(enabled))
        s.button("open", "Open", lambda: s.choose(load))
        s.button("play", "Play", movie.start)
        pause = s.button("pause", "Pause")
        pause.setCheckable(True)
        s.link(pause, "toggled(bool)", movie.setPaused)

        def stop():
            movie.stop()
            movie.jumpToFrame(0)
            pause.setChecked(False)
            refresh()

        s.button("stop", "Stop", stop)
        s.button("quit", "Quit", s.h.close)
        s.h.cleanup.insert(0, lambda: movie.stop() if not s.h.owner.closed else None)
        s.keep("load", load)
        return s.h


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_movie-a3b3cbe51c1506c6', 'Animated Checker Player')


if __name__ == "__main__":
    main()
