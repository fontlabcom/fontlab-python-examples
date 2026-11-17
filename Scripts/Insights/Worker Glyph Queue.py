# this_file: Scripts/Insights/Worker Glyph Queue.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (source grant unresolved; no code copied):
# _reference/Belsepubi_naali/bin/pymodules/localscene/localscene.py:40
"""Demonstrate worker glyph queue with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from queue import Empty, Queue
from threading import Event, Thread
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S

NAMES = ("A", "H", "O", "space")


def _produce(incoming: Queue, stop: Event) -> None:
    """Publish only plain Python data; no Qt objects enter this worker."""
    try:
        for name in NAMES:
            if stop.wait(0.03):
                return
            incoming.put_nowait(
                ("result", {"glyph": name, "name_score": sum(map(ord, name))})
            )
        incoming.put_nowait(("done", None))
    except (TypeError, ValueError) as error:
        incoming.put_nowait(("error", str(error)))


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with S.Session(qt, "Worker sample glyph audit", gui.QWidget()) as session:
        handle = session.h
        window, stop, incoming = handle.widget, Event(), Queue(maxsize=8)
        start_button = gui.QPushButton("Start sample audit", window)
        stop_button = gui.QPushButton("Stop audit", window)
        log = gui.QPlainTextEdit(window)
        log.setReadOnly(True)
        layout = gui.QVBoxLayout(window)
        for control in (start_button, stop_button, log):
            layout.addWidget(control)
        timer, worker = qt.QtCore.QTimer(window), None
        state = {"phase": "idle", "results": [], "error": ""}

        def stop_work() -> None:
            stop.set()
            if not handle.owner.closed:
                timer.stop()
            if worker is not None:
                worker.join(1.0)
                if worker.is_alive():
                    raise RuntimeError(
                        "Sample audit worker did not stop; retaining owned UI"
                    )
            if state["phase"] == "running":
                state["phase"] = "stopped"

        def start() -> None:
            nonlocal worker
            if state["phase"] == "running":
                return
            stop_work()
            while not incoming.empty():
                incoming.get_nowait()
            stop.clear()
            state.update(phase="running", results=[], error="")
            log.clear()
            worker = Thread(
                target=_produce,
                args=(incoming, stop),
                name="insight-glyph-audit",
                daemon=True,
            )
            worker.start()
            timer.start(30)

        def deliver() -> None:
            for _ in range(8):
                try:
                    kind, value = incoming.get_nowait()
                except Empty:
                    return
                if kind == "result":
                    state["results"].append(value)
                    log.appendPlainText(f"{value['glyph']}: {value['name_score']}")
                else:
                    state.update(
                        phase="done" if kind == "done" else "error", error=value or ""
                    )
                    stop_work()
                    return

        def release() -> None:
            nonlocal worker
            worker = None

        handle.cleanup.append(stop_work)
        handle.release.append(release)
        handle.connect_old(start_button, "clicked()", start)
        handle.connect_old(stop_button, "clicked()", stop_work)
        handle.connect(timer.timeout, deliver)
        handle.controls.update(
            start=start_button, stop=stop_button, timer=timer, log=log
        )
        handle.inspect_ui = lambda: {
            **state,
            "results": [dict(row) for row in state["results"]],
            "worker_alive": bool(worker and worker.is_alive()),
            "timer_active": bool(timer.isActive()),
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_worker-glyph-queue", "Worker Glyph Queue")


if __name__ == "__main__":
    main()
