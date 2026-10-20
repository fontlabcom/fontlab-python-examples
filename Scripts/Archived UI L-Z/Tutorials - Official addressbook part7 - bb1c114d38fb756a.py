# this_file: Scripts/Archived UI L-Z/Tutorials - Official addressbook part7 - bb1c114d38fb756a.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 76dfa4471b683cfa4b9c8f199fdda69033b367ff7758f88571bf65ea03eccb56
"""Launch the preserved archive entry: Tutorials - Official addressbook part7 - bb1c114d38fb756a.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/tutorials/pyqt-official/part7-bb1c114d38fb756a.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Tutorials - Official addressbook part7 - bb1c114d38fb756a.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/tutorials/pyqt-official/part7-bb1c114d38fb756a.py'
    )


if __name__ == "__main__":
    main()
