# MenuTitle: GetGo - Masters Axes and Instances
# this_file: Scripts/Archived GetGo/GetGo - Masters Axes and Instances.py
# preserved-source-sha256: b66b704bc5d5fa09b1f8d15effa09ba119973672c3db755fff20095116d4394f
"""Launch the preserved archive entry: GetGo - Masters Axes and Instances.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/getgo/designspace.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived GetGo > GetGo - Masters Axes and Instances.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/getgo/designspace.py'
    )


if __name__ == "__main__":
    main()
