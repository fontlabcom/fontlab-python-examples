# this_file: Scripts/Archived UI L-Z/Widgets - Qt Text Editor - a601a41dc5a3c23a.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: b796aaf96533d3770f1ad52a2d2a1b9535f7c4f2bd21eb27fb82d74a2bf3f204
"""Launch the preserved archive entry: Widgets - Qt Text Editor - a601a41dc5a3c23a.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/widgets/pyqt-examples/main-a601a41dc5a3c23a.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Widgets - Qt Text Editor - a601a41dc5a3c23a.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/widgets/pyqt-examples/main-a601a41dc5a3c23a.py'
    )


if __name__ == "__main__":
    main()
