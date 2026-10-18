# this_file: candidate_tests/models_candidate/conftest.py
"""Load only the candidate src package; legacy root tests remain untouched."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
