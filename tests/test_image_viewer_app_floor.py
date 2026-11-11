# this_file: tests/test_image_viewer_app_floor.py
"""Both Font Reference Image Viewers' App minimum is decided and tested (Issue 250).

The two scripts are thin facades over the same App ``qt.images.viewer.model``
module (``show`` and ``show_bounded``), so they cannot need different App
releases. The floor is the oldest App release tag that provides every API the
viewers call: both entry points (first shipped in v1.2.0) and the PythonQt
``QAction.setShortcut(QKeySequence(...))`` fix from 6ece10e that the bounded
viewer's shortcuts need in FontLab (first shipped in v1.2.4). The tag checks
read the sibling App checkout's real release tags.

The scripts still state the historical ``App>=0.2.156.dev0``: both are proposed
consolidation sources (``menu-consolidations.json``), which must stay
byte-identical until Image Viewer Lab absorbs them or the ledger is
re-baselined. ``DECIDED_FLOOR`` records the decision until then.
"""

import ast
import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT.parent / "fontlab-fontlabapp"
VIEWERS = (
    "Scripts/Tools/Font Reference Image Viewer.py",
    "Scripts/Tools/Font Reference Image Viewer - Bounded Zoom.py",
)
FLOOR = re.compile(r"\bApp>=(\d+\.\d+\.\d+(?:\.dev\d+)?)")
RELEASE = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
MODEL = "src/fontlabapp/qt/images/viewer/model.py"
CONTROLS = "src/fontlabapp/qt/images/viewer/controls.py"
DECIDED_FLOOR = "1.2.4"


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
        for tag in _git("tag").split()
        if (m := RELEASE.fullmatch(tag))
    ]
    assert tags, f"App release tags are needed from the sibling checkout {APP}"
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
