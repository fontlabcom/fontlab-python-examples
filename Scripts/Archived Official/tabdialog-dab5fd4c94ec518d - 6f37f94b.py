# this_file: Scripts/Archived Official/tabdialog-dab5fd4c94ec518d - 6f37f94b.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 6fd6f74eddf5d3579fc8b46e70fab7de6444cd70d41a2776c1ca437b345fc2bf
"""Launch the preserved archive entry: tabdialog-dab5fd4c94ec518d - 6f37f94b.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/tabdialog-dab5fd4c94ec518d.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > tabdialog-dab5fd4c94ec518d - 6f37f94b.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/tabdialog-dab5fd4c94ec518d.py'
    )


if __name__ == "__main__":
    main()
