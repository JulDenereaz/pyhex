from math import sqrt
import numpy as np

SQRT3 = sqrt(3)


def hex_tile_size(circumradius: int) -> tuple[int, int]:
    """Return (width, height) bounding box for a pointy-top hex with given circumradius."""
    w = 2 * circumradius
    h = round(SQRT3 * circumradius)
    return w, h


def make_hex_mask(width: int, height: int) -> np.ndarray:
    """
    Boolean mask [height, width] — True where the pixel is inside a pointy-top hex.

    Pointy-top hex conditions (circumradius R = width/2):
      |dy| <= R*sqrt(3)/2          (horizontal flat edges)
      |dx|*sqrt(3) + |dy| <= R*sqrt(3)   (diagonal edges)
    """
    cx = width / 2.0
    cy = height / 2.0
    R = width / 2.0

    xs = np.arange(width, dtype=float) + 0.5
    ys = (np.arange(height, dtype=float) + 0.5).reshape(-1, 1)

    dx = np.abs(xs - cx)
    dy = np.abs(ys - cy)

    flat_edge = dy <= R * SQRT3 / 2.0
    diag_edge = dx * SQRT3 + dy <= R * SQRT3

    return flat_edge & diag_edge


def hex_polygon_points(width: int, height: int) -> list[tuple[int, int]]:
    """
    Return the 6 vertex coordinates of a pointy-top hex fitting in (width, height).
    Useful for drawing an outline polygon.
    """
    cx = width / 2.0
    cy = height / 2.0
    R = width / 2.0  # circumradius (tip to center)
    r = R * SQRT3 / 2.0  # inradius (flat edge to center)

    return [
        (round(cx),          round(cy - R)),   # top
        (round(cx + r),      round(cy - R / 2)),  # top-right
        (round(cx + r),      round(cy + R / 2)),  # bottom-right
        (round(cx),          round(cy + R)),   # bottom
        (round(cx - r),      round(cy + R / 2)),  # bottom-left
        (round(cx - r),      round(cy - R / 2)),  # top-left
    ]
