# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/designer - polygonwidget-773db5c24ae98ffb.py
# preserved-source-sha256: c96726078578bad1e6651507493d0a0914a98d35b54ed0553f215c01bdcd3b57
"""Launch the preserved archive entry: designer - polygonwidget-773db5c24ae98ffb.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > designer - polygonwidget-773db5c24ae98ffb.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py'
    )


if __name__ == "__main__":
    main()
