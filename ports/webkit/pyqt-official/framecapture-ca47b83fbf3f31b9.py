# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/ca47b83fbf3f31b9.md
# this_file: ports/webkit/pyqt-official/framecapture-ca47b83fbf3f31b9.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab."
    )
