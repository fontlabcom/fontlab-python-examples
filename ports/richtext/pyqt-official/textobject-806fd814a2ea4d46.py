# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/806fd814a2ea4d46.md
# this_file: ports/richtext/pyqt-official/textobject-806fd814a2ea4d46.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QTextObjectInterface is unavailable in FontLab.")
