import numpy as np
from pyhex.state import AppState
from pyhex.tools._flood import flood_region


class FillTool:
    def on_mouse_down(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        if state.active_tile_data is None:
            return
        h, w = state.active_tile_data.shape[:2]
        if not (0 <= px < w and 0 <= py < h):
            return
        if not mask[py, px]:
            return
        fill = tuple(state.foreground_color)
        if tuple(state.active_tile_data[py, px]) == fill:
            return
        region = flood_region(px, py, state.active_tile_data, mask, w, h)
        state.active_tile_data[region] = fill
        state.dirty = True

    def on_mouse_drag(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        pass
