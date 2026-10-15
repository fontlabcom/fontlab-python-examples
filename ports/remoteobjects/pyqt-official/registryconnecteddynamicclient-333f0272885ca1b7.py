# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/333f0272885ca1b7.md
# this_file: ports/remoteobjects/pyqt-official/registryconnecteddynamicclient-333f0272885ca1b7.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtRemoteObjects host and replica bindings are unavailable in FontLab."
    )
