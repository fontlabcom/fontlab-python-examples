# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b83377c9b48aec14.md
# this_file: ports/remoteobjects/pyqt-official/registryconnecteddynamicserver-b83377c9b48aec14.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtRemoteObjects host and replica bindings are unavailable in FontLab."
    )
