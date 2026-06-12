import numpy as np
from pyhex.state import AppState


class NoiseTool:
    def on_mouse_down(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        if state.active_tile_data is None:
            return
        rng = np.random.default_rng()
        combined = mask & (rng.random(mask.shape) < 0.5)
        state.active_tile_data[combined] = state.foreground_color
        state.dirty = True

    def on_mouse_drag(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        pass
