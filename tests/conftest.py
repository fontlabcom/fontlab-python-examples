# this_file: tests/conftest.py
"""Owned source/receipt fixtures; no third-party code is imported."""

import hashlib
from pathlib import Path

import pytest


@pytest.fixture
def native_boundary(monkeypatch):
    """Launcher contract doubles only; no real FontLab or Qt is loaded."""
    from qt_doubles import fake_host

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    import fontlab_python_examples as examples

    qt, owned = fake_host(monkeypatch)
    yield qt, owned
    for name in ("QLabel", "QVBoxLayout", "Signals and Slots", "Qt Designer"):
        examples.close(name)


@pytest.fixture
def sources(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    contents = {
        "README.md": b"Examples, with licensing unspecified.\n",
        "widgets/main.py": b"from PyQt5.QtWidgets import QApplication\nfrom helper import value\nif __name__ == '__main__':\n    app = QApplication([])\n    app.exec_()\n",
        "widgets/helper.py": b"value = 3\n",
        "widgets/broken.py": b"from PyQt5 import QtCore\ndef invalid(:\n",
        "widgets/view.ui": b'<ui><widget class="QWidget" name="view"/></ui>',
        "widgets/resources.qrc": b"<RCC><qresource><file>icon.png</file></qresource></RCC>",
        "widgets/icon.png": b"owned fixture",
        "others/matplotlib/Subplot.py": b"from matplotlib import pyplot as plt\nplt.show()\n",
        "others/matplotlib/subplot.py": b"from matplotlib import pyplot as plt\nplt.show(block=True)\n",
    }
    files = {}
    tree = []
    for index, (logical, data) in enumerate(contents.items()):
        storage = f"bytes/{index}"
        (root / "bytes").mkdir(exist_ok=True)
        (root / storage).write_bytes(data)
        blob = hashlib.sha1(
            b"blob " + str(len(data)).encode() + b"\0" + data
        ).hexdigest()
        files[logical] = {
            "storage_path": storage,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_sha": blob,
        }
        tree.append(
            {
                "path": logical,
                "type": "blob",
                "sha": blob,
                "size": len(data),
                "mode": "100644",
            }
        )
    repo = "owned/examples"
    trees = {
        "repositories": [
            {
                "repository": repo,
                "commit": "a" * 40,
                "file_count": len(files),
                "python_file_count": 5,
                "tree": {"truncated": False, "tree": tree},
            }
        ]
    }
    recovery = {
        "denominator": {"repositories": 1, "source_files": len(files)},
        "repositories": [
            {
                "repository": repo,
                "commit": "a" * 40,
                "files_verified": len(files),
                "files": files,
            }
        ],
    }
    return trees, recovery, {repo: root}
