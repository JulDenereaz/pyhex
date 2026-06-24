import numpy as np
from pyhex.state import AppState
from pyhex.tools._flood import flood_region


class NoiseTool:
    def on_mouse_down(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        if state.active_tile_data is None:
            return
        h, w = state.active_tile_data.shape[:2]
        if not (0 <= px < w and 0 <= py < h):
            return
        if not mask[py, px]:
            return
        region = flood_region(px, py, state.active_tile_data, mask, w, h)
        r, g, b, a = state.foreground_color
        v = state.noise_variation
        rng = np.random.default_rng()
        # Random offset per pixel per channel, clipped to valid range
        delta = rng.integers(-v, v + 1, size=(h, w, 3), dtype=np.int16)
        base  = np.array([r, g, b], dtype=np.int16)
        colors = np.clip(base + delta, 0, 255).astype(np.uint8)
        state.active_tile_data[region, :3] = colors[region]
        state.active_tile_data[region,  3] = a
        state.dirty = True

    def on_mouse_drag(self, px: int, py: int, state: AppState, mask: np.ndarray) -> None:
        pass
