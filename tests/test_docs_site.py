# this_file: tests/test_docs_site.py
"""The standalone site generates current menus before a strict build or preview."""

import sys
from pathlib import Path

import pytest

from src_docs import build


@pytest.mark.parametrize("arguments,command", [([], "build"), (["--serve", "--offline"], "serve")])
def test_main_when_mode_is_selected_then_catalogues_before_rendering(monkeypatch, arguments, command):
    called = []
    monkeypatch.setattr(build, "catalogue", lambda root: called.append(root))
    monkeypatch.setattr(build.subprocess, "run", lambda args, **kwargs: called.append((args, kwargs)))
    monkeypatch.setattr(sys, "argv", ["build.py", *arguments])
    build.main()
    root = Path(__file__).resolve().parents[1]
    assert called == [root, (["properdocs", command, "--strict", "-f", "src_docs/mkdocs.yml"], {"cwd": root, "check": True})]


def test_main_when_catalogue_fails_then_does_not_render(monkeypatch):
    def fail(root):
        raise ValueError("invalid menu")

    monkeypatch.setattr(build, "catalogue", fail)
    monkeypatch.setattr(build.subprocess, "run", lambda *args, **kwargs: pytest.fail("must not render invalid catalogue"))
    monkeypatch.setattr(sys, "argv", ["build.py"])
    with pytest.raises(ValueError, match="invalid menu"):
        build.main()
