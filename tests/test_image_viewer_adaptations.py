# this_file: tests/test_image_viewer_adaptations.py
"""Complete distinct originals, lazy facades and exact prior43-menu source ancestry."""
import hashlib,json,runpy,sys
from pathlib import Path
from types import ModuleType
import pytest
ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('part,entry,sha',[(2,'show','03e04bedb750535fbf3bf59fc9b3d90eda75890a8731f804204da0b9af1325ca'),(3,'show_bounded','a56d05bd0de0204bb29e96995d043b9054104eb370fc80a36bc398db77a29bac')])
def test_distinct_image_viewer_source_and_real_lazy_fly_contract(monkeypatch,part,entry,sha):
 rows=json.loads((ROOT/'menu-adaptations.json').read_text())['adaptations'];row=next(r for r in rows if r.get('family')==f'image-viewer-part{part}')
 assert row['source_sha256']==sha and row['assets']==[] and not row['original_workflow_accepted'] and row['native_acceptance']=='pending'
 path=ROOT/row['menu'];assert hashlib.sha256(path.read_bytes()).hexdigest()==row['destination_sha256'] and sha in (ROOT/'NOTICE').read_text()
 calls=[]
 for name in ['fly','fly.ap','fly.ap.image_viewer']:monkeypatch.setitem(sys.modules,name,ModuleType(name))
 setattr(sys.modules['fly.ap.image_viewer'],entry,lambda:calls.append(entry))
 namespace=runpy.run_path(str(path),run_name='inspection');assert calls==[];namespace['main']();runpy.run_path(str(path),run_name='__main__');assert calls==[entry,entry]

def test_all41_prior_menus_and25_adaptation_rows_remain_exact():
 old=json.loads((ROOT/'tests/image-viewer-prior-baseline.json').read_text());assert len(old['prior_runtime'])==41 and len(old['prior_adaptations'])==25
 for name,digest in old['prior_runtime'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 rows=json.loads((ROOT/'menu-adaptations.json').read_text())['adaptations'];assert rows[:25]==old['prior_adaptations'] and len(rows)==99
