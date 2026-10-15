# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/ae16288fede27692.md
# this_file: ports/webkit/pyqt-official/simpleselector-ae16288fede27692.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab."
    )
