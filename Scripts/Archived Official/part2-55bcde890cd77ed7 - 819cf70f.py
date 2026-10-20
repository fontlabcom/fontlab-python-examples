# this_file: Scripts/Archived Official/part2-55bcde890cd77ed7 - 819cf70f.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 490ac4f490f979500d01162453793a4f5481f668034c3ff7d29129bc763998ed
"""Launch the preserved archive entry: part2-55bcde890cd77ed7 - 819cf70f.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/tutorials/pyqt-official/part2-55bcde890cd77ed7.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > part2-55bcde890cd77ed7 - 819cf70f.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/tutorials/pyqt-official/part2-55bcde890cd77ed7.py'
    )


if __name__ == "__main__":
    main()
