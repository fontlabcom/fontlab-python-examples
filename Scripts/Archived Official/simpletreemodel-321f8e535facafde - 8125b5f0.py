# this_file: Scripts/Archived Official/simpletreemodel-321f8e535facafde - 8125b5f0.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 0eb40bcaded0341ad05f3891e54ee5f06e02616d3efa03b175742863d178fc86
"""Launch the preserved archive entry: simpletreemodel-321f8e535facafde - 8125b5f0.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/simpletreemodel-321f8e535facafde.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > simpletreemodel-321f8e535facafde - 8125b5f0.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/simpletreemodel-321f8e535facafde.py'
    )


if __name__ == "__main__":
    main()
