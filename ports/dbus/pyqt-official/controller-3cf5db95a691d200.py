# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/3cf5db95a691d200.md
# this_file: ports/dbus/pyqt-official/controller-3cf5db95a691d200.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QtDBus session-bus bindings are unavailable in FontLab.")
