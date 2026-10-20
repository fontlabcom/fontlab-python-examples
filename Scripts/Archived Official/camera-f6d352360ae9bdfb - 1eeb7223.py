# this_file: Scripts/Archived Official/camera-f6d352360ae9bdfb - 1eeb7223.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 301dc4123b766e7d68ba039dbda59a861df0d3c9676aea09c1eb079927868845
"""Launch the preserved archive entry: camera-f6d352360ae9bdfb - 1eeb7223.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/multimediawidgets/pyqt-official/camera-f6d352360ae9bdfb.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > camera-f6d352360ae9bdfb - 1eeb7223.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/multimediawidgets/pyqt-official/camera-f6d352360ae9bdfb.py'
    )


if __name__ == "__main__":
    main()
