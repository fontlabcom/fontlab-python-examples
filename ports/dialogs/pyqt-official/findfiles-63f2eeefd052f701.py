# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/63f2eeefd052f701.md
# this_file: ports/dialogs/pyqt-official/findfiles-63f2eeefd052f701.py

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

import codecs
import fnmatch


def build(qt):
    with S.Session(qt, "Directory text search", qt.QtGui.QDialog()) as s:
        s.vertical()
        root = s.temp()
        (root / "example.txt").write_text(
            "A small orchard in a quiet valley.\n", encoding="utf-8"
        )
        pattern = s.combo("pattern", ["*.txt", "*"])
        pattern.setEditable(True)
        needle = s.combo("containing", ["", "orchard"])
        needle.setEditable(True)
        directory = s.combo("directory", [str(root)])
        directory.setEditable(True)
        s.button(
            "browse",
            "Browse",
            lambda: s.choose(lambda path: directory.setEditText(path), directory=True),
        )
        table = s.table("results", ["Filename", "Size (KiB)"], [])
        count = s.keep("count", s.label("0 results"))
        progress = s.keep("progress", s.alert(s.g.QProgressDialog(s.window)))
        progress.setLabelText("Reading files")
        progress.setCancelButtonText("Cancel")
        progress.hide()
        work = {
            "iterator": None,
            "stream": None,
            "decoder": None,
            "tail": "",
            "path": None,
            "found": False,
            "query": "",
            "matches": [],
        }

        def stop():
            timer.stop()
            if work["stream"] is not None:
                work["stream"].close()
                work["stream"] = None
            if work["iterator"] is not None:
                work["iterator"].close()
                work["iterator"] = None
            progress.hide()
            s.state["searching"] = False

        def append(path):
            row = int(S.value(table, "rowCount"))
            table.insertRow(row)
            for col, text in enumerate(
                [path.name, str((path.stat().st_size + 1023) // 1024)]
            ):
                table.setItem(row, col, s.g.QTableWidgetItem(text))
            work["matches"].append(str(path))
            count.setText(str(row + 1) + " results")
            s.state["matches"] = list(work["matches"])

        def step():
            if work["iterator"] is None:
                return
            try:
                if work["stream"] is None:
                    # A bounded number of directory entries per GUI turn.
                    for _ in range(32):
                        entry = next(work["iterator"])
                        if entry.is_file() and fnmatch.fnmatch(
                            entry.name, str(S.value(pattern, "currentText"))
                        ):
                            path = Path(entry.path)
                            if not work["query"]:
                                append(path)
                                return
                            try:
                                work["stream"] = path.open("rb")
                            except OSError:
                                continue
                            work.update(
                                path=path,
                                decoder=codecs.getincrementaldecoder("utf-8")(
                                    "replace"
                                ),
                                tail="",
                                found=False,
                            )
                            break
                    if work["stream"] is None:
                        return
                data = work["stream"].read(65536)
                text = work["decoder"].decode(data, final=not data)
                combined = work["tail"] + text
                work["found"] = work["found"] or work["query"] in combined
                work["tail"] = (
                    combined[-max(0, len(work["query"]) - 1) :]
                    if len(work["query"]) > 1
                    else ""
                )
                if work["found"] or not data:
                    work["stream"].close()
                    work["stream"] = None
                    if work["found"]:
                        append(work["path"])
            except StopIteration:
                stop()
            except OSError as error:
                s.state["error"] = str(error)
                if work["stream"] is not None:
                    work["stream"].close()
                    work["stream"] = None

        timer = s.timer("search_timer", 0, step, start=False)

        def begin():
            import os

            stop()
            table.setRowCount(0)
            work["matches"].clear()
            s.state["matches"] = []
            count.setText("0 results")
            try:
                work["iterator"] = os.scandir(str(S.value(directory, "currentText")))
            except OSError as error:
                s.state["error"] = str(error)
                return
            work["query"] = str(S.value(needle, "currentText"))
            s.state["searching"] = True
            progress.setRange(0, 0)
            progress.show()
            timer.start(0)

        s.button("find", "Find", begin)
        s.link(progress, "canceled()", lambda *a: stop())
        s.h.cleanup.insert(0, stop)

        def activate(row, col):
            if 0 <= row < len(work["matches"]):
                s.g.QDesktopServices.openUrl(
                    s.c.QUrl.fromLocalFile(work["matches"][row])
                )

        s.link(table, "cellActivated(int,int)", activate)
        s.keep("search", begin)
        s.keep("step", step)
        s.keep("cancel", stop)
        s.state.update(searching=False, matches=[])
        return s.h
