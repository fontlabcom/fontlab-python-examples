# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/6ed36280660df7ea.md
# this_file: ports/webkit/pyqt-official/formextractor-6ed36280660df7ea.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab."
    )
