from math import sqrt
import numpy as np

SQRT3 = sqrt(3)


def hex_tile_size(circumradius: int) -> tuple[int, int]:
    """Return (width, height) bounding box for a pointy-top hex with given circumradius.

    Pointy-top means two vertices at top and bottom → taller than wide:
      width  = sqrt(3) * R  (flat-edge to flat-edge)
      height = 2 * R        (tip to tip)
    """
    w = round(SQRT3 * circumradius)
    h = 2 * circumradius
    return w, h


def make_hex_mask(width: int, height: int) -> np.ndarray:
    """
    Boolean mask [height, width] — True where the pixel is inside a pointy-top hex.

    Pointy-top hex conditions (circumradius Rc = height/2):
      |dy| <= Rc                         (top/bottom vertex extent)
      |dx|*sqrt(3) + |dy| <= 2*Rc       (diagonal edge half-planes)
    """
    cx = width / 2.0
    cy = height / 2.0
    Rc = height / 2.0  # circumradius = half height for pointy-top

    xs = np.arange(width, dtype=float) + 0.5
    ys = (np.arange(height, dtype=float) + 0.5).reshape(-1, 1)

    dx = np.abs(xs - cx)
    dy = np.abs(ys - cy)

    top_bottom = dy <= Rc
    diag_edges = dx * SQRT3 + dy <= 2.0 * Rc

    return top_bottom & diag_edges


def hex_polygon_points(width: int, height: int) -> list[tuple[int, int]]:
    """
    Return the 6 vertex coordinates of a pointy-top hex fitting in (width, height).
    Useful for drawing an outline polygon.
    """
    cx = width / 2.0
    cy = height / 2.0
    Rc = height / 2.0   # circumradius (tip to center, vertical)
    r  = width / 2.0    # inradius (flat edge to center, horizontal)

    return [
        (round(cx),      round(cy - Rc)),       # top
        (round(cx + r),  round(cy - Rc / 2)),   # top-right
        (round(cx + r),  round(cy + Rc / 2)),   # bottom-right
        (round(cx),      round(cy + Rc)),        # bottom
        (round(cx - r),  round(cy + Rc / 2)),   # bottom-left
        (round(cx - r),  round(cy - Rc / 2)),   # top-left
    ]
