import numpy as np
from pyhex.state import AppState


class PickerTool:
    def on_mouse_down(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        if state.active_tile_data is None:
            return
        h, w = state.active_tile_data.shape[:2]
        if not (0 <= px < w and 0 <= py < h):
            return
        rgba = state.active_tile_data[py, px]
        state.foreground_color = (int(rgba[0]), int(rgba[1]), int(rgba[2]), int(rgba[3]))

    def on_mouse_drag(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        self.on_mouse_down(px, py, state, mask)
