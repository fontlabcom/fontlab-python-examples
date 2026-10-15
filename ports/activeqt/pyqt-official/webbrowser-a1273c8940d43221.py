# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/a1273c8940d43221.md
# this_file: ports/activeqt/pyqt-official/webbrowser-a1273c8940d43221.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError("QAxContainer.QAxWidget is unavailable in FontLab.")
