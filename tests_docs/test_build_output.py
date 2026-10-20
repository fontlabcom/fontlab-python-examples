# this_file: tests_docs/test_build_output.py
"""Real clean builds must preserve authored historical guides beside the site."""

from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config import load_config

ROOT = Path(__file__).resolve().parents[1]


def test_clean_build_when_project_output_used_then_authored_guides_survive_twice(
    tmp_path,
):
    project = load_config(str(ROOT / "src_docs/mkdocs.yml"))
    output = Path(project.site_dir).relative_to(ROOT)
    guides = tmp_path / "docs"
    guides.mkdir()
    guide = guides / "PRE-INTEGRATION-GUIDE.md"
    expected = b"# Owned historical guide\nKeep every byte.\n"
    guide.write_bytes(expected)
    content = tmp_path / "content"
    content.mkdir()
    (content / "index.md").write_text("# Owned local build\n")
    config_file = tmp_path / "mkdocs.yml"
    config_file.write_text(
        "site_name: Owned clean build\ndocs_dir: content\nsite_dir: "
        + output.as_posix()
        + "\nplugins: []\n"
    )
    for _ in range(2):
        config = load_config(str(config_file))
        build(config)
        assert guide.exists(), "A clean site build deleted an authored historical guide"
        assert guide.read_bytes() == expected, (
            "Clean builds must preserve authored guide bytes"
        )
        assert (Path(config.site_dir) / "index.html").exists(), (
            "The configured site still has to build"
        )
    assert output == Path(".build/site"), (
        "Keep generated output separate from tracked docs source"
    )
