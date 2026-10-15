# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/38465a8f4b1a229f.md
# this_file: ports/dbus/pyqt-official/chat-38465a8f4b1a229f.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QtDBus session-bus bindings are unavailable in FontLab.")
