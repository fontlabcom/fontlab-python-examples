# MenuTitle: Path Problem Report
# this_file: Scripts/Archived Recipes/Path Problem Report.py
# preserved-source-sha256: 083be309facb9cfa00a3973785f59c728e3f5d6b506416d9499d4cd21698f98e
"""Launch the preserved archive entry: Path Problem Report.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/glyphs_path_report/path_report.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Path Problem Report.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/recipes/glyphs_path_report/path_report.py'
    )


if __name__ == "__main__":
    main()
