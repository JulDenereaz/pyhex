import numpy as np
from pyhex.state import AppState

_VARIATION = 30   # ± per channel


class NoiseTool:
    def on_mouse_down(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        if state.active_tile_data is None:
            return
        r, g, b, a = state.foreground_color
        h, w = state.active_tile_data.shape[:2]
        rng = np.random.default_rng()
        # Random offset per pixel per channel, clipped to valid range
        delta = rng.integers(-_VARIATION, _VARIATION + 1, size=(h, w, 3), dtype=np.int16)
        base  = np.array([r, g, b], dtype=np.int16)
        colors = np.clip(base + delta, 0, 255).astype(np.uint8)
        state.active_tile_data[mask, :3] = colors[mask]
        state.active_tile_data[mask,  3] = a
        state.dirty = True

    def on_mouse_drag(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        pass
