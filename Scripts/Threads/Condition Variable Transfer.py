# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/27709a02d37b9ba9.md
# this_file: Scripts/Threads/Condition Variable Transfer.py
"""Condition Variable Transfer. Setup: FontLab 9, Fly App and Lessons; no font needed."""


from fontlab_python_lessons import qt_demos as S


def wire(handle, obj, signature, callback):
    def receive(*args):
        if not handle.owner.closed:
            callback(*args)

    handle.connect_old(obj, signature, receive)
    return receive


def button(qt, handle, layout, name, callback):
    item = qt.QtGui.QPushButton(name, handle.widget)
    layout.addWidget(item)
    handle.controls[name] = item
    wire(handle, item, "clicked()", lambda *args: callback())
    return item


def timer(qt, handle, interval, callback):
    item = qt.QtCore.QTimer(handle.widget)
    wire(handle, item, "timeout()", lambda *args: callback())
    handle.cleanup.append(item.stop)
    item.start(interval)
    return item


import queue
import threading

USE_SEMAPHORES = False
CAPACITY = 8192
TOTAL = 100000


class Transfer:
    """Two scalar-only workers with cancellation at every blocking boundary."""

    def __init__(self):
        self.cancel = threading.Event()
        self.condition = threading.Condition()
        self.free = threading.Semaphore(CAPACITY)
        self.used = threading.Semaphore(0)
        self.buffer = [""] * CAPACITY
        self.count = 0
        self.messages = queue.Queue(8)
        self.threads = [
            threading.Thread(target=self.produce, name="example-producer"),
            threading.Thread(target=self.consume, name="example-consumer"),
        ]

    def acquire(self, semaphore):
        while not self.cancel.is_set():
            if semaphore.acquire(timeout=0.02):
                return True
        return False

    def produce(self):
        for index in range(TOTAL):
            if self.cancel.is_set():
                return
            if USE_SEMAPHORES:
                if not self.acquire(self.free):
                    return
                self.buffer[index % CAPACITY] = "ACGT"[index % 4]
                self.used.release()
            else:
                with self.condition:
                    self.condition.wait_for(
                        lambda: self.count < CAPACITY or self.cancel.is_set()
                    )
                    if self.cancel.is_set():
                        return
                    self.buffer[index % CAPACITY] = "ACGT"[index % 4]
                    self.count += 1
                    self.condition.notify_all()

    def consume(self):
        chunk = []
        for index in range(TOTAL):
            if self.cancel.is_set():
                return
            if USE_SEMAPHORES:
                if not self.acquire(self.used):
                    return
                character = self.buffer[index % CAPACITY]
                self.free.release()
            else:
                with self.condition:
                    self.condition.wait_for(
                        lambda: self.count > 0 or self.cancel.is_set()
                    )
                    if self.cancel.is_set():
                        return
                    character = self.buffer[index % CAPACITY]
                    self.count -= 1
                    self.condition.notify_all()
            chunk.append(character)
            if len(chunk) == 256 or index == TOTAL - 1:
                if not self.deliver("".join(chunk)):
                    return
                chunk.clear()

    def deliver(self, text):
        while not self.cancel.is_set():
            try:
                self.messages.put(text, timeout=0.02)
                return True
            except queue.Full:
                pass
        return False

    def start(self):
        for worker in self.threads:
            worker.start()

    def stop(self):
        self.cancel.set()
        with self.condition:
            self.condition.notify_all()
        for worker in self.threads:
            if worker.ident is not None:
                worker.join(1)
                if worker.is_alive():
                    raise RuntimeError("Owned transfer worker did not stop")


def build(qt):
    with S.Session(qt, "Condition-variable transfer") as session:
        handle, layout = session.h, session.vertical()
        log = qt.QtGui.QTextEdit(handle.widget)
        log.setReadOnly(True)
        layout.addWidget(log)
        state = {"worker": None, "received": 0, "tail": ""}

        def stop():
            if state["worker"] is not None:
                state["worker"].stop()

        def start():
            stop()
            worker = Transfer()
            state.update(worker=worker, received=0, tail="")
            log.clear()
            worker.start()

        def poll():
            worker = state["worker"]
            if worker is None:
                return
            for _ in range(8):
                try:
                    text = worker.messages.get_nowait()
                except queue.Empty:
                    break
                state["received"] += len(text)
                state["tail"] = (state["tail"] + text)[-CAPACITY:]
            log.setPlainText(
                f"Consumed {state['received']} of {TOTAL}\n" + state["tail"]
            )

        button(qt, handle, layout, "Start", start)
        button(qt, handle, layout, "Stop", stop)
        handle.cleanup.append(stop)
        ticker = timer(qt, handle, 25, poll)
        handle.controls.update(
            log=log,
            start=start,
            stop=stop,
            poll=poll,
            transfer=lambda: state["worker"],
            timer=ticker,
        )
        handle.inspect_ui = lambda: {
            "received": state["received"],
            "running": bool(
                state["worker"] and any(t.is_alive() for t in state["worker"].threads)
            ),
        }
        return handle


def main():
    """Open a retained modeless menu demonstration in FontLab."""
    return S.launch(build, 'restored_waitconditions-27709a02d37b9ba9', 'Condition Variable Transfer')


if __name__ == "__main__":
    main()
