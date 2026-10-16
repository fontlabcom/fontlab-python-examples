# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/781a3a959215eb81.md
# this_file: ports/remoteobjects/pyqt-official/modelviewserver-781a3a959215eb81.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtRemoteObjects host and replica bindings are unavailable in FontLab."
    )
