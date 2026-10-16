# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/1ad60855ca28f3cc.md
# this_file: ports/opengl/pyqt-official/hellogl-1ad60855ca28f3cc.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QOpenGLContext.versionFunctions and version-specific GL wrappers are unavailable in FontLab."
    )
