# this_file: tests/test_unresolved_licence_assets_absent.py
"""The 14 unresolved licence-provenance assets stay out of the tree (Issue 250).

The 2026-10-15 closing check left 14 records with ``state: unresolved`` in
``catalog/licenses.json``: five assets byte-identical and four whitespace-equal
to Qt qtbase ``styleexample`` (5.15/6.5), and five PyQt example assets with no
traced grant. Commit d3ab76d replaced all 14 with self-authored files. Commit
9c53f92 then removed the whole ``ports/`` tree, ``catalog/licenses.json`` and the
replacement generator. Its archive is held outside this repository.

This test pins the original upstream bytes. For each asset it keeps the SHA-256
of the exact bytes and the SHA-256 with all whitespace removed. No tracked file
may sit at an original path, carry the same bytes, or match after whitespace is
removed. A reintroduced copy then fails here until its licence is recorded or
the asset is replaced.
"""

import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()

# (original target path, upstream sha256, sha256 with all whitespace removed),
# taken from d3ab76d^:catalog/licenses.json and the blobs at d3ab76d^.
UNRESOLVED = (
    (
        "ports/widgets/pyqt-examples/icon-adeb6eaa0049d0d3.svg",
        "b093adc694d5d6dd71f675063de19f16e9bd10867710d5a4eb3f7712fab1c2e1",
        "ab4fb8fdb03dff289d5e82a4cd674638ee1f63bde0739e3b7d991397a375834f",
    ),
    (
        "ports/widgets/pyqt-examples/icon-3f05f5f2d0cc6df2.svg",
        "b093adc694d5d6dd71f675063de19f16e9bd10867710d5a4eb3f7712fab1c2e1",
        "ab4fb8fdb03dff289d5e82a4cd674638ee1f63bde0739e3b7d991397a375834f",
    ),
    (
        "ports/multimedia/pyqt-examples/bullet-accab87abcc10bea.png",
        "432fb4995d6949ba0f21d8d896bf9519c7d62dac18116a8ce07b7b1feeb8b1e2",
        "f9ad501e94125fbc5c1c4ab713ac7a27eca4e289fdc2444e12f4c76589e56459",
    ),
    (
        "ports/multimedia/pyqt-examples/icon-6988c3833303e9d8.svg",
        "b093adc694d5d6dd71f675063de19f16e9bd10867710d5a4eb3f7712fab1c2e1",
        "ab4fb8fdb03dff289d5e82a4cd674638ee1f63bde0739e3b7d991397a375834f",
    ),
    (
        "ports/multimedia/pyqt-examples/shot-3d215869bc0bba5c.wav",
        "0a2eea1cdfc6524472ef7fa04a4c489e7a3ff7658e0511cad8491746a630139b",
        "bbff559db32bd777153dc6745b9199a4b5f42e3737f1cf9e6e6ec8f321934249",
    ),
    (
        "ports/embedded/eyllanesc/assets/631cc1bc310c00b9/files/add.png",
        "87e9e8e2e63a40bd8d9afd5201ebefdea0c0eb8a199bfd010c719a2b7b856503",
        "b1792bfc73c6d724367d6ca49ee6cd0ee3f6b6f02f85283c698c052b96763c17",
    ),
    (
        "ports/embedded/eyllanesc/assets/631cc1bc310c00b9/files/application.qss",
        "0de20d9a13a43d3a4cbf269c9a84ffbc3ae345d779acc2325eed6c37958fa1b5",
        "7ca8e09469a4710e35710e1d304c2b900cc82da2f2269409009a4b5aa499a9c8",
    ),
    (
        "ports/embedded/eyllanesc/assets/631cc1bc310c00b9/files/blue.qss",
        "8d1fd74573ef2ac6313aca7aae4c08f5682950467dfde037d068bc1c78d23f8d",
        "26d3e6a4338bb1c682dd56551ba17e06a794c55a68259b54eed44c5a7a6cc875",
    ),
    (
        "ports/embedded/eyllanesc/assets/631cc1bc310c00b9/files/khaki.qss",
        "11e2a7f27f84feba8264a13d15a5e0942b6f54579cde169b2b013b0c657cc96a",
        "6556070dc6d7395baf35b973ed61f6c66b90792c432a3833b68c888b8fcb5c0b",
    ),
    (
        "ports/embedded/eyllanesc/assets/631cc1bc310c00b9/files/nature_1.jpg",
        "28a43543b7afb2be1317cd06cb942013d44f6ea8b59d0304af0e949257a6e5bb",
        "78a2515976a8a83313dad89bb135c06709ca7ae3c9560dcf61e09dc67bb980e2",
    ),
    (
        "ports/embedded/eyllanesc/assets/631cc1bc310c00b9/files/nostyle.qss",
        EMPTY_SHA256,
        EMPTY_SHA256,
    ),
    (
        "ports/embedded/eyllanesc/assets/631cc1bc310c00b9/files/remove.png",
        "84ef46c3b8a67f98470224e3c5bc0932cf8294bc58b9a5370f80606c11306757",
        "b1994e20469a477a4265978c4edaf83f1639b086864ab709214abaa582d4968a",
    ),
    (
        "ports/embedded/eyllanesc/assets/631cc1bc310c00b9/files/transparent.qss",
        "275dc01d9e282e04fef7d0b47b74ec7c57acd53a8fc142d8fe379c70c4eb6c68",
        "7aa3da82a3ab53d206cf7bf8e4c41effb783ea4cfc1389263da4dd13bb2f41d7",
    ),
    (
        "ports/embedded/eyllanesc/assets/631cc1bc310c00b9/stylewidget.ui",
        "1ad413ca0a208ba353a498d4ad5b2409220b2a69a3f2f2069375dc73f0b1acfc",
        "6e71f519b58b54f92e43f0d1e8d68ef15c2c6932c27e128ec2e448d4fbf0d4b8",
    ),
)


def tracked_files(root: Path = ROOT) -> list[str]:
    """Return the repository's tracked paths, relative to ``root``."""
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True
    )
    return [p for p in out.stdout.decode().split("\0") if p]


def matches(root: Path, paths: list[str], pins: tuple = UNRESOLVED) -> list[str]:
    """Name every path or content match against the 14 unresolved assets.

    The empty ``nostyle.qss`` is checked by path only: its hash is the hash of
    every empty file.
    """
    names = {path for path, _, _ in pins}
    raw = {sha for _, sha, _ in pins if sha != EMPTY_SHA256}
    bare = {sha for _, _, sha in pins if sha != EMPTY_SHA256}
    found = []
    for rel in paths:
        if rel in names:
            found.append(f"{rel}: original path")
        file = root / rel
        if not file.is_file():
            continue
        data = file.read_bytes()
        if hashlib.sha256(data).hexdigest() in raw:
            found.append(f"{rel}: upstream bytes")
        elif hashlib.sha256(re.sub(rb"\s+", b"", data)).hexdigest() in bare:
            found.append(f"{rel}: upstream content after whitespace removal")
    return found


def test_unresolved_assets_when_tree_scanned_then_none_present():
    """No tracked file reintroduces any of the 14 unresolved assets."""
    assert matches(ROOT, tracked_files()) == [], (
        "an unresolved licence asset is back; record its licence or replace it"
    )


def test_unresolved_record_catalogue_when_tree_scanned_then_absent():
    """The catalogue that held the unresolved records is not tracked."""
    assert "catalog/licenses.json" not in tracked_files()


def test_pins_when_counted_then_fourteen_records():
    """The pins cover the 14 records from the closing check."""
    assert len(UNRESOLVED) == 14
    assert len({path for path, _, _ in UNRESOLVED}) == 14


def test_matches_when_copies_planted_then_each_kind_reported(tmp_path):
    """Path, exact-byte and whitespace-only variants are each detected."""
    path = UNRESOLVED[6][0]
    (tmp_path / path).parent.mkdir(parents=True)
    (tmp_path / path).write_bytes(b"own")
    (tmp_path / "exact.png").write_bytes(b"x")
    (tmp_path / "spaced.qss").write_bytes(b"a {}\n")
    (tmp_path / "empty.qss").write_bytes(b"")
    exact = hashlib.sha256(b"x").hexdigest()
    bare = hashlib.sha256(b"a{}").hexdigest()
    pins = (
        *UNRESOLVED,
        ("other/exact.png", exact, "0"),
        ("other/spaced.qss", "0", bare),
    )
    found = matches(tmp_path, [path, "exact.png", "spaced.qss", "empty.qss"], pins)
    assert found == [
        f"{path}: original path",
        "exact.png: upstream bytes",
        "spaced.qss: upstream content after whitespace removal",
    ]
