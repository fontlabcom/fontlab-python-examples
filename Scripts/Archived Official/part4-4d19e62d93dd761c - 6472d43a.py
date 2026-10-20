# this_file: Scripts/Archived Official/part4-4d19e62d93dd761c - 6472d43a.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: a9327f2e6fea9b64450f61fb021afd868beb20c92c376500a408a7e034531c52
"""Launch the preserved archive entry: part4-4d19e62d93dd761c - 6472d43a.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/tutorials/pyqt-official/part4-4d19e62d93dd761c.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > part4-4d19e62d93dd761c - 6472d43a.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/tutorials/pyqt-official/part4-4d19e62d93dd761c.py'
    )


if __name__ == "__main__":
    main()
