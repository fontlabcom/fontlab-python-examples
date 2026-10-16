# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/0677ebfd7fa2cc60.md
# this_file: ports/sql/pyqt-official/tablemodel-0677ebfd7fa2cc60.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtSql model and delegate bindings are unavailable in FontLab."
    )
