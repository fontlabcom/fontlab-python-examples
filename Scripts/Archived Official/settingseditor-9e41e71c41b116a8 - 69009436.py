# this_file: Scripts/Archived Official/settingseditor-9e41e71c41b116a8 - 69009436.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 1a35d9d5b3989ba7728ce129fea1bcc98cce4b221f59cf8916788ffe0ab53475
"""Launch the preserved archive entry: settingseditor-9e41e71c41b116a8 - 69009436.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/settingseditor-9e41e71c41b116a8.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > settingseditor-9e41e71c41b116a8 - 69009436.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/settingseditor-9e41e71c41b116a8.py'
    )


if __name__ == "__main__":
    main()
