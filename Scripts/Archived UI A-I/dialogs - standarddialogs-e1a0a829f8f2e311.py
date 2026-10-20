# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/dialogs - standarddialogs-e1a0a829f8f2e311.py
# preserved-source-sha256: 4a705367140cd7600706cf7ab7522523ddc7c5cd3592309c78d316b67cfc0055
"""Launch the preserved archive entry: dialogs - standarddialogs-e1a0a829f8f2e311.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/dialogs/pyqt-official/standarddialogs-e1a0a829f8f2e311.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > dialogs - standarddialogs-e1a0a829f8f2e311.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/dialogs/pyqt-official/standarddialogs-e1a0a829f8f2e311.py'
    )


if __name__ == "__main__":
    main()
