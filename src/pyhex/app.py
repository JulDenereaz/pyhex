from __future__ import annotations
import sys
import pygame
from pyhex import config
from pyhex.hex_geometry import hex_tile_size, make_hex_mask
from pyhex.tileset import Tileset
from pyhex.state import AppState
from pyhex.tools.pencil import PencilTool
from pyhex.tools.eraser import EraserTool
from pyhex.tools.fill import FillTool
from pyhex.tools.picker import PickerTool
from pyhex.views.toolbar import ToolBar
from pyhex.views.palette import ColorPalette
from pyhex.views.editor import TileEditor
from pyhex.views.overview import TilesetOverview


class Application:
    def __init__(self, tileset_path: str, tile_size: int):
        self.screen = pygame.display.set_mode(
            (config.WINDOW_W, config.WINDOW_H), pygame.RESIZABLE
        )
        pygame.display.set_caption("pyhex — Hex Tile Editor")
        self.clock = pygame.time.Clock()

        tile_w, tile_h = hex_tile_size(tile_size)
        self.state = AppState(tile_w=tile_w, tile_h=tile_h)
        self.state.tileset = Tileset(tileset_path, tile_w, tile_h)
        self.state.select_tile(0, 0)

        self.hex_mask = make_hex_mask(tile_w, tile_h)

        self.tools = {
            "pencil": PencilTool(),
            "eraser": EraserTool(),
            "fill":   FillTool(),
            "picker": PickerTool(),
        }

        font = pygame.font.SysFont(None, 20)
        self.toolbar  = ToolBar(self.state, font)
        self.palette  = ColorPalette(self.state, font)
        self.editor   = TileEditor(self.state, self.hex_mask, self.tools, font)
        self.overview = TilesetOverview(self.state, self.hex_mask, font)

    def run(self) -> None:
        while True:
            self.clock.tick(config.TARGET_FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._handle_quit()
                    return
                if not self._dispatch(event):
                    self._handle_global(event)
            self._render()
            pygame.display.flip()

    # ------------------------------------------------------------------
    def _dispatch(self, event: pygame.event.Event) -> bool:
        return (
            self.toolbar.handle_event(event)
            or self.palette.handle_event(event)
            or self.editor.handle_event(event)
            or self.overview.handle_event(event)
        )

    def _handle_global(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                self.state.save(mask=self.hex_mask)
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self.state.zoom = min(config.MAX_ZOOM, self.state.zoom + 1)
            elif event.key == pygame.K_MINUS:
                self.state.zoom = max(config.MIN_ZOOM, self.state.zoom - 1)

    def _handle_quit(self) -> None:
        if self.state.dirty:
            self.state.save(mask=self.hex_mask)

    def _render(self) -> None:
        sw, sh = self.screen.get_size()

        left_w = config.LEFT_PANEL_W
        overview_h = config.OVERVIEW_H
        toolbar_h = config.TOOLBAR_H
        editor_x = left_w
        editor_w = sw - left_w
        editor_h = sh - overview_h

        toolbar_rect  = pygame.Rect(0, 0, left_w, toolbar_h)
        palette_rect  = pygame.Rect(0, toolbar_h, left_w, editor_h - toolbar_h)
        editor_rect   = pygame.Rect(editor_x, 0, editor_w, editor_h)
        overview_rect = pygame.Rect(0, editor_h, sw, overview_h)

        self.screen.fill(config.COLOR_BG)
        self.toolbar.draw(self.screen, toolbar_rect)
        self.palette.draw(self.screen, palette_rect)
        self.editor.draw(self.screen, editor_rect)
        self.overview.draw(self.screen, overview_rect)

        # Title bar update with save hint
        title = "pyhex"
        if self.state.dirty:
            title += " *"
        title += "  |  Ctrl+S to save"
        pygame.display.set_caption(title)
