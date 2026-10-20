# this_file: Scripts/Archived Official/helloglwidget-5941e31267112c98 - ede65ffa.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: a688b6a61b2a35fec1589a713341f1df8d228069589f7c302272f6eff1d77975
"""Launch the preserved archive entry: helloglwidget-5941e31267112c98 - ede65ffa.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/designer/pyqt-official/helloglwidget-5941e31267112c98.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > helloglwidget-5941e31267112c98 - ede65ffa.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/designer/pyqt-official/helloglwidget-5941e31267112c98.py'
    )


if __name__ == "__main__":
    main()
