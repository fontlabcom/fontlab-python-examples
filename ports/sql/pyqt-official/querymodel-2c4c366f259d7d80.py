# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/2c4c366f259d7d80.md
# this_file: ports/sql/pyqt-official/querymodel-2c4c366f259d7d80.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtSql model and delegate bindings are unavailable in FontLab."
    )
