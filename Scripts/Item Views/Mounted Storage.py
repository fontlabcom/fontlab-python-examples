# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/cf15c3e91cdd8ded.md
# this_file: Scripts/Item Views/Mounted Storage.py

"""Mounted Storage: modeless PythonQt demonstration; no font data is changed."""

from fontlab_python_lessons import qt_demos as S


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


def main():
    """Open this example through the retained App dialog owner."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_storageview-cf15c3e91cdd8ded', 'Mounted Storage')


if __name__ == "__main__":
    main()
