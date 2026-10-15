# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/54cbd9afababdf71.md
# this_file: ports/remoteobjects/pyqt-official/directconnectdynamicclient-54cbd9afababdf71.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtRemoteObjects host and replica bindings are unavailable in FontLab."
    )
