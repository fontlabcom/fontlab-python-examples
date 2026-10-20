# this_file: tests_docs/test_retained_literals.py
"""Frozen first-party sources remain inert data with complete literal rendering."""
import hashlib,json
from pathlib import Path
from markdown import markdown
ROOT=Path(__file__).resolve().parents[1]


def test_frozen_inputs_when_rendered_then_source_hashes_and_python_fences_preserved():
    folder=ROOT/"src_docs/retained-insights"
    manifest=json.loads((folder/"manifest.json").read_text())
    assert len(manifest["files"])==18
    for rel,row in manifest["files"].items():
        source=ROOT/rel
        assert source.suffix==".txt" and hashlib.sha256(source.read_bytes()).hexdigest()==row["sha256"]
        content=f'```python\n--8<-- "{rel}"\n```'
        html=markdown(content,extensions=["pymdownx.snippets","pymdownx.superfences"],extension_configs={"pymdownx.snippets":{"base_path":[str(ROOT)],"check_paths":True}})
        assert "<code>" in html and "highlight" in html
    assert hashlib.sha256((folder/"LICENSE").read_bytes()).hexdigest()==manifest["license_sha256"]
