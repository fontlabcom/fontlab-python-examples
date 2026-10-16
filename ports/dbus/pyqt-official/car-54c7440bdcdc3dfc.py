# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/54c7440bdcdc3dfc.md
# this_file: ports/dbus/pyqt-official/car-54c7440bdcdc3dfc.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QtDBus session-bus bindings are unavailable in FontLab.")
