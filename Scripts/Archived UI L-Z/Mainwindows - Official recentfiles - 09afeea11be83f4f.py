# this_file: Scripts/Archived UI L-Z/Mainwindows - Official recentfiles - 09afeea11be83f4f.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 94b77a8efda276c9f64222c2cc0d77b59aedc59f1731a309ab7ad7eb29f18465
"""Launch the preserved archive entry: Mainwindows - Official recentfiles - 09afeea11be83f4f.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/mainwindows/pyqt-official/recentfiles-09afeea11be83f4f.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Mainwindows - Official recentfiles - 09afeea11be83f4f.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/mainwindows/pyqt-official/recentfiles-09afeea11be83f4f.py'
    )


if __name__ == "__main__":
    main()
