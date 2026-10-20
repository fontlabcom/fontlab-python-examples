# MenuTitle: Correct Contour Direction and Start Points
# this_file: Scripts/Archived Recipes/Correct Contour Direction and Start Points.py
# preserved-source-sha256: a429b53d76d7f78338b05fa05de2f904d19f794f15aafcee102be5fef5077278
"""Launch the preserved archive entry: Correct Contour Direction and Start Points.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/contour_direction/recipe.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Correct Contour Direction and Start Points.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/recipes/contour_direction/recipe.py'
    )


if __name__ == "__main__":
    main()
