# this_file: Scripts/Archived Reference/P3 Sources - HopeFOAM_HopeFOAM - ThirdParty-0.1 - ParaView-5.0.1 - Plugins - PythonQtPlugin - WrapPythonQt -- 12a62820f848.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 891ae8b20cbf040e0422504a7e2cd11b1fec7e75cb8a6c073fa32488213408a8
"""Launch the preserved archive entry: P3 Sources - HopeFOAM_HopeFOAM - ThirdParty-0.1 - ParaView-5.0.1 - Plugins - PythonQtPlugin - WrapPythonQt -- 12a62820f848.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/HopeFOAM_HopeFOAM/ThirdParty-0.1/ParaView-5.0.1/Plugins/PythonQtPlugin/WrapPythonQt.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - HopeFOAM_HopeFOAM - ThirdParty-0.1 - ParaView-5.0.1 - Plugins - PythonQtPlugin - WrapPythonQt -- 12a62820f848.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/HopeFOAM_HopeFOAM/ThirdParty-0.1/ParaView-5.0.1/Plugins/PythonQtPlugin/WrapPythonQt.py'
    )


if __name__ == "__main__":
    main()
