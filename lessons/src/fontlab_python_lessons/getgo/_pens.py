# this_file: lessons/src/fontlab_python_lessons/getgo/_pens.py
# SPDX-License-Identifier: Apache-2.0
"""Adapt FontLab's QPointF segment operands to the FontTools pen protocol."""

from typing import Any


def tuple_point(point: Any) -> tuple | None:
    """Detach QPointF coordinates; preserve tuples and qCurveTo's None sentinel."""
    if point is None or isinstance(point, tuple):
        return point
    return point.x(), point.y()


class TuplePen:
    """Forward segment operations with ordinary, host-free coordinate tuples."""

    def __init__(self: Any, pen: Any) -> None:
        self.pen = pen

    def moveTo(self: Any, point: Any) -> None:
        self.pen.moveTo(tuple_point(point))

    def lineTo(self: Any, point: Any) -> None:
        self.pen.lineTo(tuple_point(point))

    def curveTo(self: Any, *points: Any) -> None:
        self.pen.curveTo(*(tuple_point(point) for point in points))

    def qCurveTo(self: Any, *points: Any) -> None:
        self.pen.qCurveTo(*(tuple_point(point) for point in points))

    def closePath(self: Any) -> None:
        self.pen.closePath()

    def endPath(self: Any) -> None:
        self.pen.endPath()

    def addComponent(self: Any, name: str, transformation: tuple) -> None:
        self.pen.addComponent(name, transformation)
