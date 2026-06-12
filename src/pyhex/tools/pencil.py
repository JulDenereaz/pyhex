import numpy as np
from pyhex.state import AppState


class PencilTool:
    def on_mouse_down(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        self._draw(px, py, state, mask)

    def on_mouse_drag(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        self._draw(px, py, state, mask)

    def _draw(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        if state.active_tile_data is None:
            return
        h, w = state.active_tile_data.shape[:2]
        if not (0 <= px < w and 0 <= py < h):
            return
        if not mask[py, px]:
            return
        state.active_tile_data[py, px] = state.foreground_color
        state.dirty = True
