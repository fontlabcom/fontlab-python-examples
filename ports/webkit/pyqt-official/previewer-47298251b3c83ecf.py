# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/47298251b3c83ecf.md
# this_file: ports/webkit/pyqt-official/previewer-47298251b3c83ecf.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab."
    )
