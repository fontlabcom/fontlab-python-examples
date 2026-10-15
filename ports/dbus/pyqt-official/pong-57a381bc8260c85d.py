# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/57a381bc8260c85d.md
# this_file: ports/dbus/pyqt-official/pong-57a381bc8260c85d.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QtDBus session-bus bindings are unavailable in FontLab.")
