# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/f4000cf8ca288375.md
# this_file: ports/webkit/pyqt-official/fancybrowser-f4000cf8ca288375.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab."
    )
