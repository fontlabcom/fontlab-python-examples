# this_file: tests/test_pattern_lab_adaptation.py
"""Hash-bound full authoring workflow and lazy public Fly facade."""
import hashlib,json,runpy,sys
from pathlib import Path
from types import ModuleType
ROOT=Path(__file__).resolve().parents[1]

def test_pattern_authoring_preserves_exact_source_identity_and_public_entry(monkeypatch):
    row=next(r for r in json.loads((ROOT/'menu-adaptations.json').read_text())['adaptations'] if r.get('family')=='glyph-pattern-lab-part2')
    assert row['source']=='rescued/part2/ports/tools/pyqt-official/regexp-626fd0acec74fd91.py'
    assert row['source_sha256']=='c45e9688f256a61cbe36eb3fd91e73750dec4f08175acda54a667db37bc8823e'
    assert row['assets']==[] and row['native_acceptance']=='pending' and row['original_workflow_accepted'] is False
    path=ROOT/row['menu'];assert hashlib.sha256(path.read_bytes()).hexdigest()==row['destination_sha256']
    calls=[]
    for name in ('fly','fly.ap','fly.ap.glyph_pattern'):monkeypatch.setitem(sys.modules,name,ModuleType(name))
    sys.modules['fly.ap.glyph_pattern'].show=lambda:calls.append('show')
    entry=runpy.run_path(str(path),run_name='inspection');assert not calls
    entry['main']();runpy.run_path(str(path),run_name='__main__');assert calls==['show','show']
    assert row['source_sha256'] in (ROOT/'NOTICE').read_text()
