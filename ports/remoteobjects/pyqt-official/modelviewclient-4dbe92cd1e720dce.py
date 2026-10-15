# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/4dbe92cd1e720dce.md
# this_file: ports/remoteobjects/pyqt-official/modelviewclient-4dbe92cd1e720dce.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtRemoteObjects host and replica bindings are unavailable in FontLab."
    )
