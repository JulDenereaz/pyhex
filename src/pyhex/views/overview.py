from __future__ import annotations
import numpy as np
import pygame
from pyhex import config
from pyhex.state import AppState

TILE_PAD = 6


class TilesetOverview:
    """Panel showing all tiles in a 2D grid; click one to select for editing."""

    def __init__(self, state: AppState, mask: np.ndarray, font: pygame.font.Font):
        self.state = state
        self.mask = mask
        self.font = font
        self._rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._tile_rects: list[tuple[int, int, pygame.Rect]] = []
        self._checker_cache: dict[tuple[int, int], pygame.Surface] = {}

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row, col, r in self._tile_rects:
                if r.collidepoint(event.pos):
                    self.state.select_tile(row, col)
                    return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for row, col, r in self._tile_rects:
                if r.collidepoint(event.pos):
                    self._copy_tile(row, col)
                    return True
        return False

    def _copy_tile(self, row: int, col: int) -> None:
        if self.state.active_tile_data is None:
            return
        if (row, col) == self.state.selected_tile:
            return
        self.state.push_undo()
        self.state.active_tile_data[:] = self.state.tileset.get_tile(row, col)
        self.state.dirty = True

    def draw(self, surf: pygame.Surface, rect: pygame.Rect) -> None:
        self._rect = rect
        pygame.draw.rect(surf, config.COLOR_PANEL, rect)
        pygame.draw.rect(surf, config.COLOR_BORDER, rect, 1)

        ts = self.state.tileset
        if ts is None:
            return

        tw, th = ts.tile_w, ts.tile_h

        # Scale so the full grid of rows×cols tiles fits in the available area
        avail_w = rect.width  - TILE_PAD * (ts.cols + 1)
        avail_h = rect.height - TILE_PAD * (ts.rows + 1)
        max_tw = max(1, avail_w // ts.cols)
        max_th = max(1, avail_h // ts.rows)
        scale   = min(max_tw / tw, max_th / th)
        disp_w  = max(4, int(tw * scale))
        disp_h  = max(4, int(th * scale))

        # Centre the grid
        grid_w = ts.cols * disp_w + TILE_PAD * (ts.cols + 1)
        grid_h = ts.rows * disp_h + TILE_PAD * (ts.rows + 1)
        gx0    = rect.x + (rect.width  - grid_w) // 2
        gy0    = rect.y + (rect.height - grid_h) // 2

        self._tile_rects = []
        sel_row, sel_col = self.state.selected_tile

        checker = self._get_checker(disp_w, disp_h)

        old_clip = surf.get_clip()
        surf.set_clip(rect.inflate(-2, -2))

        for row in range(ts.rows):
            for col in range(ts.cols):
                x = gx0 + TILE_PAD + col * (disp_w + TILE_PAD)
                y = gy0 + TILE_PAD + row * (disp_h + TILE_PAD)
                tile_rect = pygame.Rect(x, y, disp_w, disp_h)
                self._tile_rects.append((row, col, tile_rect))

                # Checkerboard (transparency indicator)
                surf.blit(checker, tile_rect.topleft)

                # Tile pixels with mask applied
                tile_arr = ts.get_tile(row, col)
                tile_surf = _array_to_surface_masked(tile_arr, self.mask)
                scaled = pygame.transform.scale(tile_surf, (disp_w, disp_h))
                surf.blit(scaled, tile_rect.topleft)

                # Border / selection
                color = config.COLOR_SELECTED if (row == sel_row and col == sel_col) \
                        else config.COLOR_BORDER
                width = 2 if (row == sel_row and col == sel_col) else 1
                pygame.draw.rect(surf, color, tile_rect, width)

        surf.set_clip(old_clip)

    def _get_checker(self, w: int, h: int) -> pygame.Surface:
        key = (w, h)
        if key not in self._checker_cache:
            self._checker_cache[key] = _make_checkerboard(w, h, size=5)
        return self._checker_cache[key]


# ---------------------------------------------------------------------------
def _array_to_surface_masked(arr: np.ndarray, mask: np.ndarray) -> pygame.Surface:
    h, w = arr.shape[:2]
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.surfarray.blit_array(s, arr.transpose(1, 0, 2)[:, :, :3])
    alpha = pygame.surfarray.pixels_alpha(s)
    alpha[:] = (arr[:, :, 3] * mask).T   # zero outside-hex alpha
    del alpha
    return s


def _make_checkerboard(w: int, h: int, size: int = 5) -> pygame.Surface:
    surf = pygame.Surface((w, h))
    for row in range(h // size + 1):
        for col in range(w // size + 1):
            color = (120, 120, 120) if (row + col) % 2 == 0 else (80, 80, 80)
            r = pygame.Rect(col * size, row * size,
                            min(size, w - col * size),
                            min(size, h - row * size))
            if r.width > 0 and r.height > 0:
                pygame.draw.rect(surf, color, r)
    return surf
