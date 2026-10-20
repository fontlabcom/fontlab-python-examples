# this_file: Scripts/Archived Official/padnavigator-a58650b5461c0f48 - 49daacde.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: f6af280b00f13384566780930eb7aa33b57c5202a933315841d946fcf79cfe07
"""Launch the preserved archive entry: padnavigator-a58650b5461c0f48 - 49daacde.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > padnavigator-a58650b5461c0f48 - 49daacde.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py'
    )


if __name__ == "__main__":
    main()
