from collections import deque
import numpy as np
from pyhex.state import AppState


class FillTool:
    def on_mouse_down(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        if state.active_tile_data is None:
            return
        h, w = state.active_tile_data.shape[:2]
        if not (0 <= px < w and 0 <= py < h):
            return
        if not mask[py, px]:
            return
        target = tuple(state.active_tile_data[py, px])
        fill = tuple(state.foreground_color)
        if target == fill:
            return
        self._bfs(px, py, target, fill, state.active_tile_data, mask, w, h)
        state.dirty = True

    def on_mouse_drag(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        pass

    def _bfs(self, sx, sy, target, fill, tile, mask, w, h):
        q = deque([(sx, sy)])
        visited = np.zeros((h, w), dtype=bool)
        visited[sy, sx] = True
        while q:
            x, y = q.popleft()
            if tuple(tile[y, x]) != target:
                continue
            tile[y, x] = fill
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and not visited[ny, nx] and mask[ny, nx]:
                    visited[ny, nx] = True
                    q.append((nx, ny))
