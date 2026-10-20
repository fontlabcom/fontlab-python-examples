# this_file: Scripts/Archived UI L-Z/Widgets - Official digitalclock - 3040b9f6b267a196.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: d6c1f46efc951c302c279b04ea21a22589ee61c45254e37d7569d4f906b8b446
"""Launch the preserved archive entry: Widgets - Official digitalclock - 3040b9f6b267a196.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/widgets/pyqt-official/digitalclock-3040b9f6b267a196.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Widgets - Official digitalclock - 3040b9f6b267a196.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/widgets/pyqt-official/digitalclock-3040b9f6b267a196.py'
    )


if __name__ == "__main__":
    main()
