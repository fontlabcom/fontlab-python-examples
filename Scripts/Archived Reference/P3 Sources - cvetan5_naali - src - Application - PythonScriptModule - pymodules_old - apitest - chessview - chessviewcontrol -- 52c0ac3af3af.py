# this_file: Scripts/Archived Reference/P3 Sources - cvetan5_naali - src - Application - PythonScriptModule - pymodules_old - apitest - chessview - chessviewcontrol -- 52c0ac3af3af.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 98bb14bcecd8ca1c8587b242984c6193a2d05994957e52f39297d829fce53a99
"""Launch the preserved archive entry: P3 Sources - cvetan5_naali - src - Application - PythonScriptModule - pymodules_old - apitest - chessview - chessviewcontrol -- 52c0ac3af3af.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/cvetan5_naali/src/Application/PythonScriptModule/pymodules_old/apitest/chessview/chessviewcontrol.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - cvetan5_naali - src - Application - PythonScriptModule - pymodules_old - apitest - chessview - chessviewcontrol -- 52c0ac3af3af.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/cvetan5_naali/src/Application/PythonScriptModule/pymodules_old/apitest/chessview/chessviewcontrol.py'
    )


if __name__ == "__main__":
    main()
