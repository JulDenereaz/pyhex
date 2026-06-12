from math import sqrt
import numpy as np

SQRT3 = sqrt(3)


def hex_tile_size(tile_size: int) -> tuple[int, int]:
    """Return (width, height) — square tiles of exactly tile_size × tile_size pixels.

    --tile-size 32  →  32×32 tile  (circumradius = 16, inradius ≈ 13.9)
    --tile-size 64  →  64×64 tile  (circumradius = 32, inradius ≈ 27.7)
    """
    return tile_size, tile_size


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
