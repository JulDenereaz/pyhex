from __future__ import annotations
import numpy as np
import pygame
from pyhex import config
from pyhex.state import AppState


class TileEditor:
    """Zoomed pixel-by-pixel editor for the currently selected hex tile."""

    def __init__(self, state: AppState, mask: np.ndarray, tools: dict,
                 font: pygame.font.Font):
        self.state = state
        self.mask = mask
        self.tools = tools
        self.font = font
        self._rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._mouse_held = False
        self._last_pixel: tuple[int, int] | None = None
        self._origin: tuple[int, int] = (0, 0)
        # Both caches keyed by zoom — rebuilt only on zoom change
        self._overlay_cache: pygame.Surface | None = None
        self._boundary_cache: pygame.Surface | None = None
        self._overlay_zoom: int = -1

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.state.active_tile_data is None:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._rect.collidepoint(event.pos):
                self._mouse_held = True
                px, py = self._screen_to_pixel(event.pos)
                tool = self.tools.get(self.state.active_tool)
                if tool:
                    tool.on_mouse_down(px, py, self.state, self.mask)
                self._last_pixel = (px, py)
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._mouse_held = False
            self._last_pixel = None

        if event.type == pygame.MOUSEMOTION and self._mouse_held:
            if self._rect.collidepoint(event.pos):
                px, py = self._screen_to_pixel(event.pos)
                if (px, py) != self._last_pixel:
                    tool = self.tools.get(self.state.active_tool)
                    if tool:
                        tool.on_mouse_drag(px, py, self.state, self.mask)
                    self._last_pixel = (px, py)
                return True

        if event.type == pygame.MOUSEWHEEL and self._rect.collidepoint(pygame.mouse.get_pos()):
            self.state.zoom = max(config.MIN_ZOOM,
                                  min(config.MAX_ZOOM, self.state.zoom + event.y))
            return True

        return False

    # ------------------------------------------------------------------
    def draw(self, surf: pygame.Surface, rect: pygame.Rect) -> None:
        self._rect = rect
        pygame.draw.rect(surf, config.COLOR_BG, rect)
        pygame.draw.rect(surf, config.COLOR_BORDER, rect, 1)

        tile = self.state.active_tile_data
        if tile is None:
            msg = self.font.render("Click a tile below to edit", True, config.COLOR_TEXT)
            surf.blit(msg, (rect.centerx - msg.get_width() // 2,
                            rect.centery - msg.get_height() // 2))
            return

        zoom = self.state.zoom
        th, tw = tile.shape[:2]
        scaled_w = tw * zoom
        scaled_h = th * zoom

        ox = rect.x + (rect.width - scaled_w) // 2 + self.state.editor_offset[0]
        oy = rect.y + (rect.height - scaled_h) // 2 + self.state.editor_offset[1]
        self._origin = (ox, oy)

        clip_rect = rect.inflate(-2, -2)
        old_clip = surf.get_clip()
        surf.set_clip(clip_rect)

        # 1. Tile pixels — outside-hex alpha forced to 0 so corners are invisible
        tile_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
        pygame.surfarray.blit_array(tile_surf, tile.transpose(1, 0, 2)[:, :, :3])
        alpha = pygame.surfarray.pixels_alpha(tile_surf)
        alpha[:] = (tile[:, :, 3] * self.mask).T   # zero out outside-hex alpha
        del alpha
        scaled = pygame.transform.scale(tile_surf, (scaled_w, scaled_h))
        surf.blit(scaled, (ox, oy))

        # 2. Pixel grid inside hex (zoom >= 4)
        if zoom >= 4:
            for gx in range(tw + 1):
                sx = ox + gx * zoom
                pygame.draw.line(surf, config.COLOR_GRID,
                                 (sx, max(oy, clip_rect.top)),
                                 (sx, min(oy + scaled_h, clip_rect.bottom)), 1)
            for gy in range(th + 1):
                sy = oy + gy * zoom
                pygame.draw.line(surf, config.COLOR_GRID,
                                 (max(ox, clip_rect.left), sy),
                                 (min(ox + scaled_w, clip_rect.right), sy), 1)

        # 3. Outside-hex opaque overlay + pixel-perfect boundary (numpy-cached per zoom)
        self._build_caches(zoom)
        surf.blit(self._overlay_cache,  (ox, oy))
        surf.blit(self._boundary_cache, (ox, oy))

        surf.set_clip(old_clip)

        # Status labels (drawn outside clip so they're always visible)
        zlabel = self.font.render(
            f"Zoom: {zoom}x  (scroll to zoom)", True, config.COLOR_TEXT)
        surf.blit(zlabel, (rect.x + 6, rect.bottom - zlabel.get_height() - 4))

        if self.state.dirty:
            dlabel = self.font.render("● unsaved", True, config.COLOR_DIRTY)
            surf.blit(dlabel, (rect.right - dlabel.get_width() - 6,
                               rect.bottom - dlabel.get_height() - 4))

    # ------------------------------------------------------------------
    def _build_caches(self, zoom: int) -> None:
        """Build (and cache) the overlay and pixel-perfect boundary for the given zoom."""
        if self._overlay_zoom == zoom and self._overlay_cache is not None:
            return

        th, tw = self.mask.shape
        H, W = th * zoom, tw * zoom

        # --- outside-hex overlay (nearly opaque) ---
        outside_big = np.repeat(
            np.repeat((~self.mask).astype(np.uint8), zoom, axis=0), zoom, axis=1
        )
        arr_ov = np.zeros((H, W, 4), dtype=np.uint8)
        arr_ov[outside_big.astype(bool), 3] = 215

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.surfarray.blit_array(ov, arr_ov.transpose(1, 0, 2)[:, :, :3])
        pygame.surfarray.pixels_alpha(ov)[:] = arr_ov[:, :, 3].T

        # --- pixel-perfect boundary derived from the mask ---
        # A pixel is on the boundary if inside AND has at least one outside 4-neighbor
        left  = np.pad(self.mask[:, :-1], ((0, 0), (1, 0)), constant_values=False)
        right = np.pad(self.mask[:, 1:],  ((0, 0), (0, 1)), constant_values=False)
        up    = np.pad(self.mask[:-1, :], ((1, 0), (0, 0)), constant_values=False)
        down  = np.pad(self.mask[1:,  :], ((0, 1), (0, 0)), constant_values=False)
        boundary = self.mask & ~(left & right & up & down)

        boundary_big = np.repeat(
            np.repeat(boundary.astype(np.uint8), zoom, axis=0), zoom, axis=1
        )
        r, g, b = config.COLOR_HEX_BORDER
        arr_bnd = np.zeros((H, W, 4), dtype=np.uint8)
        arr_bnd[boundary_big.astype(bool)] = [r, g, b, 255]

        bnd = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.surfarray.blit_array(bnd, arr_bnd.transpose(1, 0, 2)[:, :, :3])
        pygame.surfarray.pixels_alpha(bnd)[:] = arr_bnd[:, :, 3].T

        self._overlay_cache   = ov
        self._boundary_cache  = bnd
        self._overlay_zoom    = zoom

    def _screen_to_pixel(self, pos: tuple[int, int]) -> tuple[int, int]:
        ox, oy = self._origin
        zoom = self.state.zoom
        return (pos[0] - ox) // zoom, (pos[1] - oy) // zoom
