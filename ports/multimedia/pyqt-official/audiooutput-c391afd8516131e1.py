# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c391afd8516131e1.md
# this_file: ports/multimedia/pyqt-official/audiooutput-c391afd8516131e1.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QtMultimedia audio bindings are unavailable in FontLab.")
