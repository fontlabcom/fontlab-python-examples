# this_file: Scripts/Archived Official/pong-57a381bc8260c85d - acf20e7d.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 149d01b4e5bad67ffe3434a59d6697ee9282b7125fc069e6bd79952773db520d
"""Launch the preserved archive entry: pong-57a381bc8260c85d - acf20e7d.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/pong-57a381bc8260c85d.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > pong-57a381bc8260c85d - acf20e7d.
Result: The helper runs the preserved entry. Its source determines any window,
output or font changes. Missing resources or unsupported APIs can raise errors.

Compatibility: Native FontLab compatibility is pending. Preserved sources have
not been certified by this launcher; Python syntax and route checks do not
establish successful UI behavior or font results.
"""

from pathlib import Path


def main() -> None:
    """Dispatch this preserved entry once when explicitly launched."""
    from fly.ap.rescued_examples import launch

    launch(
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/pong-57a381bc8260c85d.py'
    )


if __name__ == "__main__":
    main()
