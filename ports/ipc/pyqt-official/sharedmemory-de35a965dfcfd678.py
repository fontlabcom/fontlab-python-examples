# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/de35a965dfcfd678.md
# this_file: ports/ipc/pyqt-official/sharedmemory-de35a965dfcfd678.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QSharedMemory lacks detach and a documented usable byte buffer in FontLab."
    )
