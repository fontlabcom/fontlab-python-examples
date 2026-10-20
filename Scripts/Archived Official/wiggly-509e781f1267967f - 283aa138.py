# this_file: Scripts/Archived Official/wiggly-509e781f1267967f - 283aa138.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: b75f1ae5b664998b0be94f3b5fe3a35b673499f3c72a827122639f9d3cab6f12
"""Launch the preserved archive entry: wiggly-509e781f1267967f - 283aa138.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/wiggly-509e781f1267967f.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > wiggly-509e781f1267967f - 283aa138.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/wiggly-509e781f1267967f.py'
    )


if __name__ == "__main__":
    main()
