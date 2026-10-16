# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/cf15c3e91cdd8ded.md
# this_file: ports/itemviews/pyqt-official/storageview-cf15c3e91cdd8ded.py

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


def human_size(size):
    number = float(size)
    for suffix in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if abs(number) < 1024 or suffix == "TiB":
            return f"{number:.1f} {suffix}"
        number /= 1024


def build(qt):
    with S.Session(qt, "Mounted storage (read only)") as s:
        s.vertical()
        table = s.table(
            "volumes",
            [
                "Root",
                "Name",
                "Device",
                "Filesystem",
                "Capacity",
                "Free",
                "Available",
                "Ready",
                "Read only",
                "Root volume",
            ],
            [],
        )
        s.state.update(loading=True, rows=[])

        def load():
            rows = []
            for volume in s.c.QStorageInfo.mountedVolumes():
                rows.append(
                    [
                        str(volume.rootPath()),
                        str(volume.displayName()),
                        str(volume.device()),
                        str(volume.fileSystemType()),
                        human_size(volume.bytesTotal()),
                        human_size(volume.bytesFree()),
                        human_size(volume.bytesAvailable()),
                        str(volume.isReady()),
                        str(volume.isReadOnly()),
                        str(volume.isRoot()),
                    ]
                )
            table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, text in enumerate(row):
                    item = s.g.QTableWidgetItem(text)
                    item.setFlags(s.c.Qt.ItemIsEnabled | s.c.Qt.ItemIsSelectable)
                    table.setItem(r, c, item)
            s.state.update(loading=False, rows=rows)

        s.timer("load_timer", 0, load, single=True)
        s.keep("load", load)
        return s.h
