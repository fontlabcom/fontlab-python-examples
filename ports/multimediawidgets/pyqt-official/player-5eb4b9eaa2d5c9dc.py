# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/5eb4b9eaa2d5c9dc.md
# this_file: ports/multimediawidgets/pyqt-official/player-5eb4b9eaa2d5c9dc.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtMultimedia and QtMultimediaWidgets media bindings are unavailable in FontLab."
    )
