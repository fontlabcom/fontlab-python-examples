# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/74af8d8d2d7774b8.md
# this_file: ports/multimedia/pyqt-official/audiodevices-74af8d8d2d7774b8.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QtMultimedia audio bindings are unavailable in FontLab.")
