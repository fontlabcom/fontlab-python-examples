# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/2f1e2f679775d89e.md
# this_file: ports/remoteobjects/pyqt-official/directconnectdynamicserver-2f1e2f679775d89e.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtRemoteObjects host and replica bindings are unavailable in FontLab."
    )
