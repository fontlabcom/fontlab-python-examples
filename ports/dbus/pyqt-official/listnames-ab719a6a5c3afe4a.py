# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/ab719a6a5c3afe4a.md
# this_file: ports/dbus/pyqt-official/listnames-ab719a6a5c3afe4a.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QtDBus session-bus bindings are unavailable in FontLab.")
