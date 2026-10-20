# this_file: Scripts/Archived Official/controller-3cf5db95a691d200 - d0c04a8a.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 54924bf7f36c1d5f53a27934785703fdb9610a80d5f00d3a16173be7d5b59ee8
"""Launch the preserved archive entry: controller-3cf5db95a691d200 - d0c04a8a.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/controller-3cf5db95a691d200.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > controller-3cf5db95a691d200 - d0c04a8a.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/controller-3cf5db95a691d200.py'
    )


if __name__ == "__main__":
    main()
