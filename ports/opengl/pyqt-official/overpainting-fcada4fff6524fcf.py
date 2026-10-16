# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/fcada4fff6524fcf.md
# this_file: ports/opengl/pyqt-official/overpainting-fcada4fff6524fcf.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QOpenGLContext.versionFunctions and version-specific GL wrappers are unavailable in FontLab."
    )
