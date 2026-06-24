from math import sqrt
import numpy as np

SQRT3 = sqrt(3)


def hex_tile_size(tile_size: int) -> tuple[int, int]:
    """Return (width, height) — square tiles of tile_size × tile_size pixels.

    Flat-top orientation: left/right vertices, top/bottom flat edges.
    --tile-size 32  →  32×32  (Rc=16)
    --tile-size 64  →  64×64  (Rc=32)
    """
    return tile_size, tile_size


def make_hex_mask(width: int, height: int) -> np.ndarray:
    """
    Boolean mask [height, width] — True where the pixel is inside a flat-top
    hex centred in the (width × height) bounding box, stretched to fill the
    full tile width AND full tile height.

    Circumradius Rc = width/2  (left/right vertices at tile edges).
    Inradius      r  = height/2 (top/bottom flat edges at tile edges).

    For a square tile r = Rc, giving a squished (non-regular) hex.
    General diagonal condition:  Rc*|dy| + 2*r*|dx| <= 2*r*Rc
    With r = Rc this simplifies to: |dy| + 2*|dx| <= 2*Rc
    """
    cx = width  / 2.0
    cy = height / 2.0
    Rc = width  / 2.0   # circumradius (left/right vertex distance from centre)
    r  = height / 2.0   # inradius    (top/bottom flat-edge distance from centre)

    xs = np.arange(width,  dtype=float) + 0.5
    ys = (np.arange(height, dtype=float) + 0.5).reshape(-1, 1)

    dx = np.abs(xs - cx)
    dy = np.abs(ys - cy)

    lateral    = dx <= Rc                                        # left/right vertex extent
    top_bottom = dy <= r                                         # top/bottom flat-edge extent
    # Corner is at (Rc/2, r) — a tile-edge coordinate, 0.5px from nearest pixel
    # centre.  Adding 0.5*Rc closes the 1-pixel gap that appears in tiled grids.
    diag_edges = Rc * dy + 2 * r * dx <= 2 * r * Rc + 0.5 * Rc

    return lateral & top_bottom & diag_edges


def hex_polygon_points(width: int, height: int) -> list[tuple[int, int]]:
    """Return the 6 vertex coordinates of a flat-top stretched hex."""
    cx = width  / 2.0
    cy = height / 2.0
    Rc = width  / 2.0   # circumradius (horizontal)
    r  = height / 2.0   # inradius    (vertical)

    return [
        (round(cx + Rc),      round(cy)),           # right vertex
        (round(cx + Rc / 2),  round(cy - r)),       # top-right corner
        (round(cx - Rc / 2),  round(cy - r)),       # top-left corner
        (round(cx - Rc),      round(cy)),            # left vertex
        (round(cx - Rc / 2),  round(cy + r)),       # bottom-left corner
        (round(cx + Rc / 2),  round(cy + r)),       # bottom-right corner
    ]
