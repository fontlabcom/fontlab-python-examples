# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/9030a87a532b8d8f.md
# this_file: ports/sql/pyqt-official/relationaltablemodel-9030a87a532b8d8f.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtSql model and delegate bindings are unavailable in FontLab."
    )
