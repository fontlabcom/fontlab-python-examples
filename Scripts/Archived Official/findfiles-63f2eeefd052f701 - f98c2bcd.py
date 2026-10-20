# this_file: Scripts/Archived Official/findfiles-63f2eeefd052f701 - f98c2bcd.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: d53e4871dcd3e6e3a8c901b07ec99db769a65265e4e3539bc68ffb721bbe20d6
"""Launch the preserved archive entry: findfiles-63f2eeefd052f701 - f98c2bcd.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/findfiles-63f2eeefd052f701.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > findfiles-63f2eeefd052f701 - f98c2bcd.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/findfiles-63f2eeefd052f701.py'
    )


if __name__ == "__main__":
    main()
