# this_file: Scripts/Archived Official/formextractor-6ed36280660df7ea - f64e75ff.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: b7c787401ac12c06fc6e0d955b6bc9bcca00eae2a37ca94b9f0da914f056b10b
"""Launch the preserved archive entry: formextractor-6ed36280660df7ea - f64e75ff.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/webkit/pyqt-official/formextractor-6ed36280660df7ea.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > formextractor-6ed36280660df7ea - f64e75ff.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/webkit/pyqt-official/formextractor-6ed36280660df7ea.py'
    )


if __name__ == "__main__":
    main()
