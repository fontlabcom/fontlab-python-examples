# this_file: Scripts/Archived Official/valuesource-738a22ef3062ed51 - 831d2178.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 92d28200fb31c2bc433069973ec8b38098257ed3d89cd07e34a59be6b3670489
"""Launch the preserved archive entry: valuesource-738a22ef3062ed51 - 831d2178.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/valuesource-738a22ef3062ed51.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > valuesource-738a22ef3062ed51 - 831d2178.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/valuesource-738a22ef3062ed51.py'
    )


if __name__ == "__main__":
    main()
