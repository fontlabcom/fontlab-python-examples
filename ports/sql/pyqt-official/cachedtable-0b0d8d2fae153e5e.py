# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/0b0d8d2fae153e5e.md
# this_file: ports/sql/pyqt-official/cachedtable-0b0d8d2fae153e5e.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtSql model and delegate bindings are unavailable in FontLab."
    )
