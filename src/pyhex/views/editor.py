from __future__ import annotations
import numpy as np
import pygame
from pyhex import config
from pyhex.state import AppState

RULER  = 22   # px width of ruler strips (left + top)
STATUS = 20   # px height of status bar at bottom

_RULER_BG   = (35, 35, 35)
_RULER_TICK = (90, 90, 90)
_RULER_TEXT = (155, 155, 155)


class TileEditor:
    """Zoomed pixel-by-pixel editor for the currently selected hex tile."""

    def __init__(self, state: AppState, mask: np.ndarray, tools: dict,
                 font: pygame.font.Font):
        self.state = state
        self.mask  = mask
        self.tools = tools
        self.font  = font
        self._ruler_font = pygame.font.SysFont(None, 13)
        self._rect:  pygame.Rect       = pygame.Rect(0, 0, 0, 0)
        self._origin: tuple[int, int]  = (0, 0)

        # Left-mouse drawing
        self._mouse_held  = False
        self._last_pixel: tuple[int, int] | None = None

        # Middle-mouse pan
        self._panning   = False
        self._pan_last: tuple[int, int] = (0, 0)

        # Hover coordinate for display
        self._hover_pixel: tuple[int, int] | None = None

        # Numpy-cached overlay + boundary (rebuilt only on zoom change)
        self._overlay_cache:  pygame.Surface | None = None
        self._boundary_cache: pygame.Surface | None = None
        self._overlay_zoom:   int = -1

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.state.active_tile_data is None:
            return False

        # ---- middle mouse → pan ----
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            if self._rect.collidepoint(event.pos):
                self._panning = True
                self._pan_last = event.pos
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            self._panning = False

        # ---- left mouse → draw ----
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

        # ---- mouse motion ----
        if event.type == pygame.MOUSEMOTION:
            # Always update hover coordinate
            if self._rect.collidepoint(event.pos):
                px, py = self._screen_to_pixel(event.pos)
                tile = self.state.active_tile_data
                if tile is not None:
                    th, tw = tile.shape[:2]
                    self._hover_pixel = (px, py) if 0 <= px < tw and 0 <= py < th else None
                else:
                    self._hover_pixel = None
            else:
                self._hover_pixel = None

            if self._panning:
                dx = event.pos[0] - self._pan_last[0]
                dy = event.pos[1] - self._pan_last[1]
                self.state.editor_offset[0] += dx
                self.state.editor_offset[1] += dy
                self._pan_last = event.pos
                return True

            if self._mouse_held and self._rect.collidepoint(event.pos):
                px, py = self._screen_to_pixel(event.pos)
                if (px, py) != self._last_pixel:
                    tool = self.tools.get(self.state.active_tool)
                    if tool:
                        tool.on_mouse_drag(px, py, self.state, self.mask)
                    self._last_pixel = (px, py)
                return True

        # ---- scroll wheel → zoom ----
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

        # Inner drawing area excludes ruler strips and status bar
        inner = pygame.Rect(rect.x + RULER, rect.y + RULER,
                            rect.width  - RULER,
                            rect.height - RULER - STATUS)

        ox = inner.x + (inner.width  - scaled_w) // 2 + self.state.editor_offset[0]
        oy = inner.y + (inner.height - scaled_h) // 2 + self.state.editor_offset[1]
        self._origin = (ox, oy)

        clip_rect = inner.inflate(-2, -2)
        old_clip  = surf.get_clip()
        surf.set_clip(clip_rect)

        # 1. Tile pixels (outside-hex alpha → 0)
        tile_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
        pygame.surfarray.blit_array(tile_surf, tile.transpose(1, 0, 2)[:, :, :3])
        alpha = pygame.surfarray.pixels_alpha(tile_surf)
        alpha[:] = (tile[:, :, 3] * self.mask).T
        del alpha
        scaled = pygame.transform.scale(tile_surf, (scaled_w, scaled_h))
        surf.blit(scaled, (ox, oy))

        # 2. Pixel grid (zoom >= 4)
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

        # 3. Outside-hex overlay + pixel-perfect hex boundary
        self._build_caches(zoom)
        surf.blit(self._overlay_cache,  (ox, oy))
        surf.blit(self._boundary_cache, (ox, oy))

        # 4. Cursor highlight on hovered pixel
        if self._hover_pixel is not None:
            hx, hy = self._hover_pixel
            hl = pygame.Surface((zoom, zoom), pygame.SRCALPHA)
            hl.fill((255, 255, 255, 55))
            surf.blit(hl, (ox + hx * zoom, oy + hy * zoom))

        surf.set_clip(old_clip)

        # 5. Rulers — drawn after clip reset so they paint over tile edges
        self._draw_rulers(surf, rect, ox, oy, tw, th, zoom)

        # 6. Status bar
        zoom_lbl = self.font.render(f"Zoom {zoom}x", True, config.COLOR_TEXT)
        surf.blit(zoom_lbl, (rect.x + RULER + 4, rect.bottom - STATUS + 2))

        if self._hover_pixel is not None:
            hx, hy = self._hover_pixel
            coord = self.font.render(f"x:{hx}  y:{hy}", True, config.COLOR_TEXT)
            surf.blit(coord, (rect.x + RULER + 80, rect.bottom - STATUS + 2))

        if self.state.dirty:
            dlabel = self.font.render("● unsaved", True, config.COLOR_DIRTY)
            surf.blit(dlabel, (rect.right - dlabel.get_width() - 6,
                               rect.bottom - STATUS + 2))

    # ------------------------------------------------------------------
    def _draw_rulers(self, surf: pygame.Surface, rect: pygame.Rect,
                     ox: int, oy: int, tw: int, th: int, zoom: int) -> None:
        top_strip  = pygame.Rect(rect.x, rect.y,          rect.width,          RULER)
        left_strip = pygame.Rect(rect.x, rect.y + RULER,  RULER, rect.height - RULER - STATUS)

        pygame.draw.rect(surf, _RULER_BG,         top_strip)
        pygame.draw.rect(surf, _RULER_BG,         left_strip)
        pygame.draw.rect(surf, config.COLOR_BORDER, top_strip,  1)
        pygame.draw.rect(surf, config.COLOR_BORDER, left_strip, 1)

        # Label step: smallest power of 2 so that step*zoom >= 28px
        step = 1
        while step * zoom < 28:
            step *= 2

        # X ruler — ticks at pixel column boundaries
        for px in range(tw + 1):
            sx = ox + px * zoom
            if not (rect.x + RULER <= sx <= rect.right):
                continue
            if px % step == 0:
                pygame.draw.line(surf, _RULER_TICK,
                                 (sx, rect.y + RULER - 7), (sx, rect.y + RULER - 1))
                lbl = self._ruler_font.render(str(px), True, _RULER_TEXT)
                surf.blit(lbl, (sx - lbl.get_width() // 2, rect.y + 2))
            else:
                pygame.draw.line(surf, _RULER_TICK,
                                 (sx, rect.y + RULER - 4), (sx, rect.y + RULER - 1))

        # Y ruler — ticks at pixel row boundaries
        for py in range(th + 1):
            sy = oy + py * zoom
            if not (rect.y + RULER <= sy <= rect.bottom - STATUS):
                continue
            if py % step == 0:
                pygame.draw.line(surf, _RULER_TICK,
                                 (rect.x + RULER - 7, sy), (rect.x + RULER - 1, sy))
                lbl = self._ruler_font.render(str(py), True, _RULER_TEXT)
                surf.blit(lbl, (rect.x + 1, sy - lbl.get_height() // 2))
            else:
                pygame.draw.line(surf, _RULER_TICK,
                                 (rect.x + RULER - 4, sy), (rect.x + RULER - 1, sy))

    # ------------------------------------------------------------------
    def _build_caches(self, zoom: int) -> None:
        """Build (and cache) the overlay and pixel-perfect boundary for the given zoom."""
        if self._overlay_zoom == zoom and self._overlay_cache is not None:
            return

        th, tw = self.mask.shape
        H, W   = th * zoom, tw * zoom

        # Outside-hex overlay (nearly opaque dark)
        outside_big = np.repeat(
            np.repeat((~self.mask).astype(np.uint8), zoom, axis=0), zoom, axis=1)
        arr_ov = np.zeros((H, W, 4), dtype=np.uint8)
        arr_ov[outside_big.astype(bool), 3] = 215

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.surfarray.blit_array(ov, arr_ov.transpose(1, 0, 2)[:, :, :3])
        pygame.surfarray.pixels_alpha(ov)[:] = arr_ov[:, :, 3].T

        # Boundary ring: OUTSIDE pixels adjacent to the hex interior.
        # Sitting on the dark overlay means it never covers drawable pixels.
        left_in  = np.pad(self.mask[:, :-1], ((0, 0), (1, 0)), constant_values=False)
        right_in = np.pad(self.mask[:, 1:],  ((0, 0), (0, 1)), constant_values=False)
        up_in    = np.pad(self.mask[:-1, :], ((1, 0), (0, 0)), constant_values=False)
        down_in  = np.pad(self.mask[1:,  :], ((0, 1), (0, 0)), constant_values=False)
        boundary = (~self.mask) & (left_in | right_in | up_in | down_in)

        boundary_big = np.repeat(
            np.repeat(boundary.astype(np.uint8), zoom, axis=0), zoom, axis=1)
        r, g, b = config.COLOR_HEX_BORDER
        arr_bnd = np.zeros((H, W, 4), dtype=np.uint8)
        arr_bnd[boundary_big.astype(bool)] = [r, g, b, 255]

        bnd = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.surfarray.blit_array(bnd, arr_bnd.transpose(1, 0, 2)[:, :, :3])
        pygame.surfarray.pixels_alpha(bnd)[:] = arr_bnd[:, :, 3].T

        self._overlay_cache  = ov
        self._boundary_cache = bnd
        self._overlay_zoom   = zoom

    # ------------------------------------------------------------------
    def _screen_to_pixel(self, pos: tuple[int, int]) -> tuple[int, int]:
        ox, oy = self._origin
        zoom   = self.state.zoom
        return (pos[0] - ox) // zoom, (pos[1] - oy) // zoom
