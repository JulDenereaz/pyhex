import pygame
from pyhex import config
from pyhex.state import AppState

SWATCH_SIZE = 18
SWATCH_PAD = 2
SWATCHES_PER_ROW = 8

SLIDER_H = 12
SLIDER_PAD = 4


class ColorPalette:
    def __init__(self, state: AppState, font: pygame.font.Font):
        self.state = state
        self.font = font
        self._swatch_rects: list[pygame.Rect] = []
        self._slider_rects: dict[str, pygame.Rect] = {}
        self._dragging_slider: str | None = None

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._swatch_rects):
                if r.collidepoint(event.pos):
                    r_val, g_val, b_val = config.PALETTE[i]
                    state = self.state
                    state.foreground_color = (r_val, g_val, b_val, state.foreground_color[3])
                    return True
            for ch, sr in self._slider_rects.items():
                if sr.collidepoint(event.pos):
                    self._dragging_slider = ch
                    self._update_slider(ch, event.pos[0], sr)
                    return True

        if event.type == pygame.MOUSEBUTTONUP:
            if self._dragging_slider:
                self._dragging_slider = None
                return True

        if event.type == pygame.MOUSEMOTION and self._dragging_slider:
            ch = self._dragging_slider
            sr = self._slider_rects.get(ch)
            if sr:
                self._update_slider(ch, event.pos[0], sr)
            return True

        return False

    def _update_slider(self, channel: str, mouse_x: int, sr: pygame.Rect) -> None:
        t = max(0.0, min(1.0, (mouse_x - sr.x) / sr.width))
        val = round(t * 255)
        r, g, b, a = self.state.foreground_color
        if channel == "R":
            self.state.foreground_color = (val, g, b, a)
        elif channel == "G":
            self.state.foreground_color = (r, val, b, a)
        elif channel == "B":
            self.state.foreground_color = (r, g, val, a)

    def draw(self, surf: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surf, config.COLOR_PANEL, rect)
        pygame.draw.rect(surf, config.COLOR_BORDER, rect, 1)

        x = rect.x + SWATCH_PAD
        y = rect.y + SWATCH_PAD

        label = self.font.render("Palette", True, config.COLOR_TEXT)
        surf.blit(label, (x, y))
        y += label.get_height() + SWATCH_PAD

        # Swatches
        self._swatch_rects = []
        for i, color in enumerate(config.PALETTE):
            col_idx = i % SWATCHES_PER_ROW
            row_idx = i // SWATCHES_PER_ROW
            sx = x + col_idx * (SWATCH_SIZE + SWATCH_PAD)
            sy = y + row_idx * (SWATCH_SIZE + SWATCH_PAD)
            r = pygame.Rect(sx, sy, SWATCH_SIZE, SWATCH_SIZE)
            self._swatch_rects.append(r)
            pygame.draw.rect(surf, color, r)
            pygame.draw.rect(surf, config.COLOR_BORDER, r, 1)

        rows = (len(config.PALETTE) + SWATCHES_PER_ROW - 1) // SWATCHES_PER_ROW
        y += rows * (SWATCH_SIZE + SWATCH_PAD) + SWATCH_PAD * 2

        # Current color preview
        preview_rect = pygame.Rect(x, y, rect.width - SWATCH_PAD * 2, 28)
        # checkerboard for alpha visibility
        _draw_checkerboard(surf, preview_rect)
        fg = self.state.foreground_color
        fg_surf = pygame.Surface((preview_rect.width, preview_rect.height), pygame.SRCALPHA)
        fg_surf.fill(fg)
        surf.blit(fg_surf, preview_rect.topleft)
        pygame.draw.rect(surf, config.COLOR_BORDER, preview_rect, 1)
        y += preview_rect.height + SWATCH_PAD * 2

        # RGB sliders
        self._slider_rects = {}
        slider_w = rect.width - SWATCH_PAD * 4
        for ch, val in zip("RGB", fg[:3]):
            ch_label = self.font.render(f"{ch}", True, config.COLOR_TEXT)
            surf.blit(ch_label, (x, y))
            sx = x + 14
            sr = pygame.Rect(sx, y + 2, slider_w - 14, SLIDER_H)
            self._slider_rects[ch] = sr
            pygame.draw.rect(surf, config.COLOR_BG, sr)
            fill_w = round(sr.width * val / 255)
            ch_color = {"R": (200, 60, 60), "G": (60, 200, 60), "B": (60, 60, 200)}[ch]
            if fill_w > 0:
                pygame.draw.rect(surf, ch_color, pygame.Rect(sr.x, sr.y, fill_w, sr.height))
            pygame.draw.rect(surf, config.COLOR_BORDER, sr, 1)
            y += SLIDER_H + SLIDER_PAD + 2

        # Hex color label
        hex_str = "#{:02X}{:02X}{:02X}".format(*fg[:3])
        hex_label = self.font.render(hex_str, True, config.COLOR_TEXT)
        surf.blit(hex_label, (x, y))


def _draw_checkerboard(surf: pygame.Surface, rect: pygame.Rect, size: int = 7) -> None:
    for row in range(rect.height // size + 1):
        for col in range(rect.width // size + 1):
            color = (160, 160, 160) if (row + col) % 2 == 0 else (100, 100, 100)
            cr = pygame.Rect(
                rect.x + col * size,
                rect.y + row * size,
                min(size, rect.right - (rect.x + col * size)),
                min(size, rect.bottom - (rect.y + row * size)),
            )
            if cr.width > 0 and cr.height > 0:
                pygame.draw.rect(surf, color, cr)
