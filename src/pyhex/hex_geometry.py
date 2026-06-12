from math import sqrt
import numpy as np

SQRT3 = sqrt(3)


def hex_tile_size(circumradius: int) -> tuple[int, int]:
    """Return (width, height) bounding box for a pointy-top hex.

    Tiles are square (2R × 2R) so the hex is centred with transparent padding
    on the sides.  circumradius=32 → 64×64 tiles, 4×4 tileset = 256×256.
    """
    size = 2 * circumradius
    return size, size


def make_hex_mask(width: int, height: int) -> np.ndarray:
    """
    Boolean mask [height, width] — True where the pixel is inside a pointy-top
    hex centred in the (width × height) bounding box.

    Three half-plane conditions (circumradius Rc = height/2):
      |dy| <= Rc                          top/bottom vertex extent
      |dx| <= Rc * sqrt(3)/2              left/right flat-edge extent
      |dx|*sqrt(3) + |dy| <= 2*Rc        diagonal edges
    """
    cx = width  / 2.0
    cy = height / 2.0
    Rc = height / 2.0

    xs = np.arange(width,  dtype=float) + 0.5
    ys = (np.arange(height, dtype=float) + 0.5).reshape(-1, 1)

    dx = np.abs(xs - cx)
    dy = np.abs(ys - cy)

    top_bottom = dy <= Rc
    lateral    = dx <= Rc * SQRT3 / 2.0   # flat vertical edges
    diag_edges = dx + SQRT3 * dy <= SQRT3 * Rc  # pointy top/bottom

    return top_bottom & lateral & diag_edges


def hex_polygon_points(width: int, height: int) -> list[tuple[int, int]]:
    """
    Return the 6 vertex coordinates of a pointy-top hex centred in (width, height).
    Always uses the geometric inradius so the polygon matches the mask exactly.
    """
    cx = width  / 2.0
    cy = height / 2.0
    Rc = height / 2.0          # circumradius
    r  = Rc * SQRT3 / 2.0     # true inradius (flat edge to centre)

    return [
        (round(cx),      round(cy - Rc)),       # top
        (round(cx + r),  round(cy - Rc / 2)),   # top-right
        (round(cx + r),  round(cy + Rc / 2)),   # bottom-right
        (round(cx),      round(cy + Rc)),        # bottom
        (round(cx - r),  round(cy + Rc / 2)),   # bottom-left
        (round(cx - r),  round(cy - Rc / 2)),   # top-left
    ]
