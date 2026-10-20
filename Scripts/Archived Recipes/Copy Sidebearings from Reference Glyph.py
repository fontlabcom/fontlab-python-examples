# MenuTitle: Copy Sidebearings from Reference Glyph
# this_file: Scripts/Archived Recipes/Copy Sidebearings from Reference Glyph.py
# preserved-source-sha256: 6aadc9ae8fb5fe615d58cba6b632b599083659c42b2a3f76c01b44814bc4ae42
"""Launch the preserved archive entry: Copy Sidebearings from Reference Glyph.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/sidebearings_from_reference/recipe.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Copy Sidebearings from Reference Glyph.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/recipes/sidebearings_from_reference/recipe.py'
    )


if __name__ == "__main__":
    main()
