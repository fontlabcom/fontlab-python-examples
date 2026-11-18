# this_file: tests/test_image_viewer_app_floor.py
"""Both Font Reference Image Viewers' App minimum is decided and tested (Issue 250).

The two scripts are thin facades over the same App ``qt.images.viewer.model``
module (``show`` and ``show_bounded``), so they cannot need different App
releases. The floor is the oldest App release tag that provides every API the
viewers call: both entry points (first shipped in v1.2.0) and the PythonQt
``QAction.setShortcut(QKeySequence(...))`` fix from 6ece10e that the bounded
viewer's shortcuts need in FontLab (first shipped in v1.2.4). The maintained App
history was squashed at v1.2.28 (2026-11-16). The tag check reads releases
reachable from the App checkout's HEAD, where v1.2.28 is the earliest release.

The scripts retain their historical setup text. ``DECIDED_FLOOR`` records the
reviewed release requirement separately until that setup text is updated.
"""

import ast
import os
import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = os.environ.get("EXAMPLES_APP_SOURCE")
APP = Path(APP_SOURCE).resolve().parents[1] if APP_SOURCE else ROOT.parent / "fontlab-fontlabapp"
VIEWERS = (
    "Scripts/Tools/Font Reference Image Viewer.py",
    "Scripts/Tools/Font Reference Image Viewer - Bounded Zoom.py",
)
FLOOR = re.compile(r"\bApp>=(\d+\.\d+\.\d+(?:\.dev\d+)?)")
RELEASE = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
MODEL = "src/fontlabapp/qt/images/viewer/model.py"
CONTROLS = "src/fontlabapp/qt/images/viewer/controls.py"
DECIDED_FLOOR = "1.2.28"


def _floors(relative: str) -> list[str]:
    tree = ast.parse((ROOT / relative).read_text())
    return FLOOR.findall(ast.get_docstring(tree) or "")


def _version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split(".")[:3])


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(APP), *args], capture_output=True, text=True, check=False
    )
    return result.stdout if result.returncode == 0 else ""


def _release_tags() -> list[tuple[tuple[int, ...], str]]:
    tags = [
        (tuple(map(int, m.groups())), tag)
        for tag in _git("tag", "--merged", "HEAD").split()
        if (m := RELEASE.fullmatch(tag))
    ]
    assert tags, f"App checkout {APP} needs release tags reachable from HEAD"
    return sorted(tags)


def _provides_viewer_api(tag: str) -> bool:
    model, controls = _git("show", f"{tag}:{MODEL}"), _git("show", f"{tag}:{CONTROLS}")
    entry_points = re.search(r"^def show\(", model, re.MULTILINE) and re.search(
        r"^def show_bounded\(", model, re.MULTILINE
    )
    return bool(entry_points) and "setShortcut(gui.QKeySequence(shortcut))" in controls


def test_viewers_when_setup_read_then_each_states_exactly_one_app_floor() -> None:
    for relative in VIEWERS:
        assert len(_floors(relative)) == 1, f"{relative} must state one App floor"


def test_viewers_when_compared_then_they_state_the_same_app_floor() -> None:
    plain, bounded = (_floors(relative) for relative in VIEWERS)
    assert plain == bounded, f"viewer App floors differ: {plain} vs {bounded}"


def test_decided_floor_when_compared_with_pyproject_then_it_is_not_below_the_install_floor() -> (
    None
):
    dependencies = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"][
        "fontlab-install"
    ]["dependencies"]
    package = next(
        dep.split(">=", 1)[1]
        for dep in dependencies
        if dep.startswith("fontlab-fontlabapp>=")
    )
    floor = DECIDED_FLOOR
    assert _version(floor) >= _version(package), (
        f"decided floor App>={floor} is below the [tool.fontlab-install] App>={package}"
    )


def test_decided_floor_when_compared_with_app_tags_then_it_is_the_oldest_release_with_every_api() -> (
    None
):
    floor = _version(DECIDED_FLOOR)
    tags = _release_tags()
    providing = [version for version, tag in tags if _provides_viewer_api(tag)]
    assert providing, "no App release tag provides the viewer API"
    assert floor == providing[0], (
        f"oldest App release with the viewer API is {providing[0]}, DECIDED_FLOOR states {floor}"
    )
