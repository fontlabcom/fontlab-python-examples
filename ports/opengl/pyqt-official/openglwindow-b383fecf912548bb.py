# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b383fecf912548bb.md
# this_file: ports/opengl/pyqt-official/openglwindow-b383fecf912548bb.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QOpenGLContext.versionFunctions and version-specific GL wrappers are unavailable in FontLab."
    )
