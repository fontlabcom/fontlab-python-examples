# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/a57a89e523c75b7f.md
# this_file: ports/multimediawidgets/pyqt-official/videographicsitem-a57a89e523c75b7f.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtMultimedia and QtMultimediaWidgets media bindings are unavailable in FontLab."
    )
