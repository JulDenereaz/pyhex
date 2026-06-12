from __future__ import annotations
import numpy as np
import pygame
from pyhex import config
from pyhex.state import AppState

TILE_PAD = 4
LABEL_H = 18


class TilesetOverview:
    """Bottom strip showing all tiles; click one to select it for editing."""

    def __init__(self, state: AppState, mask: np.ndarray, font: pygame.font.Font):
        self.state = state
        self.mask = mask
        self.font = font
        self._rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._tile_rects: list[tuple[int, int, pygame.Rect]] = []  # (row, col, rect)
        self._scroll_x = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row, col, r in self._tile_rects:
                if r.collidepoint(event.pos):
                    self.state.select_tile(row, col)
                    return True

        if event.type == pygame.MOUSEWHEEL and self._rect.collidepoint(pygame.mouse.get_pos()):
            self._scroll_x -= event.y * 20
            self._scroll_x = max(0, self._scroll_x)
            return True

        return False

    def draw(self, surf: pygame.Surface, rect: pygame.Rect) -> None:
        self._rect = rect
        pygame.draw.rect(surf, config.COLOR_PANEL, rect)
        pygame.draw.rect(surf, config.COLOR_BORDER, rect, 1)

        ts = self.state.tileset
        if ts is None:
            return

        tw, th = ts.tile_w, ts.tile_h

        # Scale tiles to fit the strip height minus label
        avail_h = rect.height - LABEL_H - TILE_PAD * 2
        scale = avail_h / th if th > 0 else 1.0
        disp_w = round(tw * scale)
        disp_h = round(th * scale)

        self._tile_rects = []
        x = rect.x + TILE_PAD - self._scroll_x
        y = rect.y + TILE_PAD + LABEL_H

        old_clip = surf.get_clip()
        surf.set_clip(rect.inflate(-2, -2))

        sel_row, sel_col = self.state.selected_tile

        for row in range(ts.rows):
            for col in range(ts.cols):
                tile_arr = ts.get_tile(row, col)
                tile_surf = _array_to_surface(tile_arr)
                scaled = pygame.transform.scale(tile_surf, (disp_w, disp_h))

                tile_rect = pygame.Rect(x, y, disp_w, disp_h)
                self._tile_rects.append((row, col, tile_rect))

                # Checkerboard background
                _draw_checkerboard(surf, tile_rect, 5)
                surf.blit(scaled, tile_rect.topleft)

                # Selection highlight
                if row == sel_row and col == sel_col:
                    pygame.draw.rect(surf, config.COLOR_SELECTED, tile_rect, 2)
                else:
                    pygame.draw.rect(surf, config.COLOR_BORDER, tile_rect, 1)

                # Label
                lbl = self.font.render(f"{row},{col}", True, config.COLOR_TEXT)
                surf.blit(lbl, (x, rect.y + TILE_PAD))

                x += disp_w + TILE_PAD

        surf.set_clip(old_clip)


def _array_to_surface(arr: np.ndarray) -> pygame.Surface:
    h, w = arr.shape[:2]
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.surfarray.blit_array(s, arr.transpose(1, 0, 2)[:, :, :3])
    pygame.surfarray.pixels_alpha(s)[:] = arr[:, :, 3].T
    return s


def _draw_checkerboard(surf: pygame.Surface, rect: pygame.Rect, size: int = 5) -> None:
    for row in range(rect.height // size + 1):
        for col in range(rect.width // size + 1):
            color = (120, 120, 120) if (row + col) % 2 == 0 else (80, 80, 80)
            cr = pygame.Rect(
                rect.x + col * size, rect.y + row * size,
                min(size, rect.right - rect.x - col * size),
                min(size, rect.bottom - rect.y - row * size),
            )
            if cr.width > 0 and cr.height > 0:
                pygame.draw.rect(surf, color, cr)
