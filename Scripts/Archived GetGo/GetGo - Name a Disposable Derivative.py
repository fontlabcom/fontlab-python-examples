# MenuTitle: GetGo - Name a Disposable Derivative
# this_file: Scripts/Archived GetGo/GetGo - Name a Disposable Derivative.py
# preserved-source-sha256: 923c9109b994eed66c18e4056cc1ed2054748bcb1a3b53083097583f1f909d40
"""Launch the preserved archive entry: GetGo - Name a Disposable Derivative.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/getgo/naming.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived GetGo > GetGo - Name a Disposable Derivative.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/getgo/naming.py'
    )


if __name__ == "__main__":
    main()
