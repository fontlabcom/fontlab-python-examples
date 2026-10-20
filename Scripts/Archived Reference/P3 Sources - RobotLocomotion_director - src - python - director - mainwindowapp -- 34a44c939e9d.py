# this_file: Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - director - mainwindowapp -- 34a44c939e9d.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 842d3b0fcb201d3681ea0670a7f875ce830232b75f48b79b844b0c098ae9b91f
"""Launch the preserved archive entry: P3 Sources - RobotLocomotion_director - src - python - director - mainwindowapp -- 34a44c939e9d.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/RobotLocomotion_director/src/python/director/mainwindowapp.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - RobotLocomotion_director - src - python - director - mainwindowapp -- 34a44c939e9d.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/RobotLocomotion_director/src/python/director/mainwindowapp.py'
    )


if __name__ == "__main__":
    main()
