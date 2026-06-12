from __future__ import annotations
import numpy as np
import pygame
from pyhex import config
from pyhex.hex_geometry import hex_polygon_points
from pyhex.state import AppState


class TileEditor:
    """Zoomed pixel-by-pixel editor for the currently selected hex tile."""

    def __init__(self, state: AppState, mask: np.ndarray, tools: dict):
        self.state = state
        self.mask = mask
        self.tools = tools
        self._rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._mouse_held = False
        self._last_pixel: tuple[int, int] | None = None

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

        # Zoom with mouse wheel
        if event.type == pygame.MOUSEWHEEL and self._rect.collidepoint(pygame.mouse.get_pos()):
            self.state.zoom = max(config.MIN_ZOOM, min(config.MAX_ZOOM,
                                                        self.state.zoom + event.y))
            return True

        return False

    def draw(self, surf: pygame.Surface, rect: pygame.Rect) -> None:
        self._rect = rect
        pygame.draw.rect(surf, config.COLOR_BG, rect)
        pygame.draw.rect(surf, config.COLOR_BORDER, rect, 1)

        tile = self.state.active_tile_data
        if tile is None:
            msg = pygame.font.SysFont(None, 24).render(
                "Click a tile below to edit", True, config.COLOR_TEXT)
            surf.blit(msg, (rect.centerx - msg.get_width() // 2,
                            rect.centery - msg.get_height() // 2))
            return

        zoom = self.state.zoom
        th, tw = tile.shape[:2]
        scaled_w = tw * zoom
        scaled_h = th * zoom

        # Center tile in editor rect
        ox = rect.x + (rect.width - scaled_w) // 2 + self.state.editor_offset[0]
        oy = rect.y + (rect.height - scaled_h) // 2 + self.state.editor_offset[1]
        self._origin = (ox, oy)

        # Draw pixels
        tile_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
        pygame.surfarray.blit_array(tile_surf, tile.transpose(1, 0, 2)[:, :, :3])
        # Handle alpha separately
        alpha_arr = tile[:, :, 3].T
        pygame.surfarray.pixels_alpha(tile_surf)[:] = alpha_arr
        scaled = pygame.transform.scale(tile_surf, (scaled_w, scaled_h))

        # Clip to editor rect
        clip_rect = rect.inflate(-2, -2)
        old_clip = surf.get_clip()
        surf.set_clip(clip_rect)
        surf.blit(scaled, (ox, oy))

        # Pixel grid (only when zoom >= 4)
        if zoom >= 4:
            for gx in range(tw + 1):
                sx = ox + gx * zoom
                pygame.draw.line(surf, config.COLOR_GRID, (sx, max(oy, clip_rect.top)),
                                 (sx, min(oy + scaled_h, clip_rect.bottom)), 1)
            for gy in range(th + 1):
                sy = oy + gy * zoom
                pygame.draw.line(surf, config.COLOR_GRID, (max(ox, clip_rect.left), sy),
                                 (min(ox + scaled_w, clip_rect.right), sy), 1)

        # Hex boundary outline
        pts = hex_polygon_points(tw, th)
        scaled_pts = [(ox + px * zoom, oy + py * zoom) for px, py in pts]
        if len(scaled_pts) >= 3:
            pygame.draw.polygon(surf, config.COLOR_HEX_BORDER, scaled_pts, 2)

        surf.set_clip(old_clip)

        # Outside-hex overlay (dim non-editable area)
        self._draw_mask_overlay(surf, clip_rect, ox, oy, tw, th, zoom)

        # Zoom label
        font = pygame.font.SysFont(None, 20)
        zlabel = font.render(f"Zoom: {zoom}x  (scroll to zoom)", True, config.COLOR_TEXT)
        surf.blit(zlabel, (rect.x + 6, rect.bottom - zlabel.get_height() - 4))

        # Dirty indicator
        if self.state.dirty:
            dlabel = font.render("● unsaved", True, config.COLOR_DIRTY)
            surf.blit(dlabel, (rect.right - dlabel.get_width() - 6,
                               rect.bottom - dlabel.get_height() - 4))

    def _draw_mask_overlay(self, surf, clip_rect, ox, oy, tw, th, zoom):
        """Draw a semi-transparent overlay on pixels outside the hex mask."""
        overlay = pygame.Surface((tw * zoom, th * zoom), pygame.SRCALPHA)
        for py in range(th):
            for px in range(tw):
                if not self.mask[py, px]:
                    pygame.draw.rect(overlay, (0, 0, 0, 120),
                                     (px * zoom, py * zoom, zoom, zoom))
        old_clip = surf.get_clip()
        surf.set_clip(clip_rect)
        surf.blit(overlay, (ox, oy))
        surf.set_clip(old_clip)

    def _screen_to_pixel(self, pos: tuple[int, int]) -> tuple[int, int]:
        ox, oy = getattr(self, "_origin", (self._rect.x, self._rect.y))
        zoom = self.state.zoom
        px = (pos[0] - ox) // zoom
        py = (pos[1] - oy) // zoom
        return px, py
