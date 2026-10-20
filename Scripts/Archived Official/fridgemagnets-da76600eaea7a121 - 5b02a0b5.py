# this_file: Scripts/Archived Official/fridgemagnets-da76600eaea7a121 - 5b02a0b5.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: b657e3128b0ad28f9576a502e00746424992ec1ad845fd6c2fbe2348399b93e0
"""Launch the preserved archive entry: fridgemagnets-da76600eaea7a121 - 5b02a0b5.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/draganddrop/pyqt-official/fridgemagnets-da76600eaea7a121.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > fridgemagnets-da76600eaea7a121 - 5b02a0b5.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/draganddrop/pyqt-official/fridgemagnets-da76600eaea7a121.py'
    )


if __name__ == "__main__":
    main()
