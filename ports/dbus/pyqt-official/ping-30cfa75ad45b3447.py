# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/30cfa75ad45b3447.md
# this_file: ports/dbus/pyqt-official/ping-30cfa75ad45b3447.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QtDBus session-bus bindings are unavailable in FontLab.")
