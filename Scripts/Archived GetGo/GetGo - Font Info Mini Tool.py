# MenuTitle: GetGo - Font Info Mini Tool
# this_file: Scripts/Archived GetGo/GetGo - Font Info Mini Tool.py
# preserved-source-sha256: b2574dfef010e55be3ae347d2695c3c69f0137548a666902d3ce3221902b1c5f
"""Launch the preserved archive entry: GetGo - Font Info Mini Tool.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/getgo/font_info_ui.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived GetGo > GetGo - Font Info Mini Tool.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/getgo/font_info_ui.py'
    )


if __name__ == "__main__":
    main()
