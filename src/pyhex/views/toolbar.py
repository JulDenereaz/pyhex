import pygame
from pyhex import config
from pyhex.state import AppState

TOOLS = [
    ("pencil", "Pencil", "P"),
    ("eraser", "Eraser", "E"),
    ("fill",   "Fill",   "F"),
    ("picker", "Picker", "K"),
    ("noise",  "Noise",  "N"),
]

BTN_H   = 24
BTN_PAD = 4
BAR_H   = 8   # slider track height


class ToolBar:
    def __init__(self, state: AppState, font: pygame.font.Font):
        self.state = state
        self.font  = font
        self._rects: dict[str, pygame.Rect] = {}
        self._slider_rect   = pygame.Rect(0, 0, 0, 0)
        self._dragging_slider = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        # ---- tool buttons ----
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self._rects.items():
                if rect.collidepoint(event.pos):
                    self.state.active_tool = name
                    return True
            # variation slider (only when noise active)
            if self.state.active_tool == "noise" and \
               self._slider_rect.collidepoint(event.pos):
                self._dragging_slider = True
                self._apply_slider(event.pos[0])
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging_slider = False

        if event.type == pygame.MOUSEMOTION and self._dragging_slider:
            self._apply_slider(event.pos[0])
            return True

        if event.type == pygame.KEYDOWN:
            key_map = {pygame.K_p: "pencil", pygame.K_e: "eraser",
                       pygame.K_f: "fill",   pygame.K_k: "picker",
                       pygame.K_n: "noise"}
            if event.key in key_map:
                self.state.active_tool = key_map[event.key]
                return True
        return False

    def draw(self, surf: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surf, config.COLOR_PANEL, rect)
        pygame.draw.rect(surf, config.COLOR_BORDER, rect, 1)

        x = rect.x + BTN_PAD
        y = rect.y + BTN_PAD

        label = self.font.render("Tools", True, config.COLOR_TEXT)
        surf.blit(label, (x, y))
        y += label.get_height() + BTN_PAD

        btn_w = rect.width - BTN_PAD * 2
        for name, display, shortcut in TOOLS:
            btn_rect = pygame.Rect(x, y, btn_w, BTN_H)
            self._rects[name] = btn_rect
            active = self.state.active_tool == name
            color  = config.COLOR_SELECTED if active else config.COLOR_HOVER
            pygame.draw.rect(surf, color, btn_rect, border_radius=3)
            pygame.draw.rect(surf, config.COLOR_BORDER, btn_rect, 1, border_radius=3)
            text = self.font.render(f"{display}  [{shortcut}]", True, config.COLOR_TEXT)
            surf.blit(text, (x + 6, y + (BTN_H - text.get_height()) // 2))
            y += BTN_H + BTN_PAD

        # Variation slider — only when noise tool is selected
        if self.state.active_tool == "noise":
            y += BTN_PAD
            lbl = self.font.render(
                f"Variation: {self.state.noise_variation}", True, config.COLOR_TEXT)
            surf.blit(lbl, (x, y))
            y += lbl.get_height() + 4

            bar = pygame.Rect(x, y, btn_w, BAR_H)
            self._slider_rect = bar
            pygame.draw.rect(surf, config.COLOR_HOVER, bar, border_radius=4)
            fill_w = max(BAR_H, int(btn_w * self.state.noise_variation / 100))
            pygame.draw.rect(surf, config.COLOR_SELECTED,
                             pygame.Rect(bar.x, bar.y, fill_w, BAR_H), border_radius=4)
            pygame.draw.rect(surf, config.COLOR_BORDER, bar, 1, border_radius=4)

    # ------------------------------------------------------------------
    def _apply_slider(self, mouse_x: int) -> None:
        if self._slider_rect.width == 0:
            return
        t = (mouse_x - self._slider_rect.x) / self._slider_rect.width
        self.state.noise_variation = max(1, min(100, int(t * 100)))
