# this_file: Scripts/Archived Official/qtdemo-85a56a1f3c25ccca - be4c6af0.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: d5d4689ba9fb3647505034c9795e2980e74194385127c8a6049240e81c5aa707
"""Launch the preserved archive entry: qtdemo-85a56a1f3c25ccca - be4c6af0.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/qtdemo/pyqt-official/qtdemo-85a56a1f3c25ccca.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > qtdemo-85a56a1f3c25ccca - be4c6af0.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/qtdemo/pyqt-official/qtdemo-85a56a1f3c25ccca.py'
    )


if __name__ == "__main__":
    main()
