# this_file: Scripts/Archived Official/movie-a3b3cbe51c1506c6 - 6ec51b04.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 9c05a79ec3dcb20214e5b43b5d543c4cba665a31fabfe54d11c998c4397303ac
"""Launch the preserved archive entry: movie-a3b3cbe51c1506c6 - 6ec51b04.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/movie-a3b3cbe51c1506c6.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > movie-a3b3cbe51c1506c6 - 6ec51b04.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/movie-a3b3cbe51c1506c6.py'
    )


if __name__ == "__main__":
    main()
