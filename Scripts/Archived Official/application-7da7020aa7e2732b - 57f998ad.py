# this_file: Scripts/Archived Official/application-7da7020aa7e2732b - 57f998ad.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 0b2bf313d85ad67cc32ca0df6a6a2e0a05a5a77b158524b91ff6f64a214e442a
"""Launch the preserved archive entry: application-7da7020aa7e2732b - 57f998ad.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/application-7da7020aa7e2732b.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > application-7da7020aa7e2732b - 57f998ad.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/application-7da7020aa7e2732b.py'
    )


if __name__ == "__main__":
    main()
