from collections import deque
import numpy as np


def flood_region(sx: int, sy: int, tile: np.ndarray, mask: np.ndarray, w: int, h: int) -> np.ndarray:
    """Boolean mask of the pixels reachable from (sx, sy) that share its color, within mask."""
    target = tuple(tile[sy, sx])
    region = np.zeros((h, w), dtype=bool)
    visited = np.zeros((h, w), dtype=bool)
    visited[sy, sx] = True
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        if tuple(tile[y, x]) != target:
            continue
        region[y, x] = True
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[ny, nx] and mask[ny, nx]:
                visited[ny, nx] = True
                q.append((nx, ny))
    return region
