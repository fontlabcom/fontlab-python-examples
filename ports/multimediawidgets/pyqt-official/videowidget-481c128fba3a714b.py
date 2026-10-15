# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/481c128fba3a714b.md
# this_file: ports/multimediawidgets/pyqt-official/videowidget-481c128fba3a714b.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtMultimedia and QtMultimediaWidgets media bindings are unavailable in FontLab."
    )
