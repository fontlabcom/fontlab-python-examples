# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/4d24cd77c74a8801.md
# this_file: ports/designer/pyqt-official/analogclock-4d24cd77c74a8801.py

import importlib.util
import sys
from pathlib import Path

_key = "fontlab_cleanroom_a_primitives"
if _key not in sys.modules:
    _path = (
        Path(__file__).resolve().parents[2]
        / "layouts/pyqt-official/basiclayouts-2f94fe07de765888.py"
    )
    _spec = importlib.util.spec_from_file_location(_key, _path)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_key] = _module
    try:
        _spec.loader.exec_module(_module)
    except BaseException:
        sys.modules.pop(_key, None)
        raise
S = sys.modules[_key]


def build(qt):
    return S.port("widgets/pyqt-official/analogclock-d6dc56a5318ffe71.py").clock(
        qt, designer=True, shaped=False
    )
