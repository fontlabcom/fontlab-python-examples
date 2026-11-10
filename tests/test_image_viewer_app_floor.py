# this_file: tests/test_image_viewer_app_floor.py
"""Both Font Reference Image Viewers state one, well-formed App floor (Issue 250).

The two scripts are thin facades over the same App ``qt.images.viewer.model``
module (``show`` and ``show_bounded``), so they cannot need different App
releases. The number itself is a historical development version; whether it
is the true minimum is not decidable from tags (App tags jump from v0.2.26 to
v1.0.0) and stays an open TODO.
"""

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWERS = (
    "Scripts/Tools/Font Reference Image Viewer.py",
    "Scripts/Tools/Font Reference Image Viewer - Bounded Zoom.py",
)
FLOOR = re.compile(r"\bApp>=(\d+\.\d+\.\d+(?:\.dev\d+)?)")


def _floors(relative: str) -> list[str]:
    tree = ast.parse((ROOT / relative).read_text())
    return FLOOR.findall(ast.get_docstring(tree) or "")


def test_viewers_when_setup_read_then_each_states_exactly_one_app_floor() -> None:
    for relative in VIEWERS:
        assert len(_floors(relative)) == 1, f"{relative} must state one App floor"


def test_viewers_when_compared_then_they_state_the_same_app_floor() -> None:
    plain, bounded = (_floors(relative) for relative in VIEWERS)
    assert plain == bounded, f"viewer App floors differ: {plain} vs {bounded}"
