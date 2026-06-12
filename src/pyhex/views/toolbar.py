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

BTN_H = 24
BTN_PAD = 4


class ToolBar:
    def __init__(self, state: AppState, font: pygame.font.Font):
        self.state = state
        self.font = font
        self._rects: dict[str, pygame.Rect] = {}

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self._rects.items():
                if rect.collidepoint(event.pos):
                    self.state.active_tool = name
                    return True
        if event.type == pygame.KEYDOWN:
            key_map = {pygame.K_p: "pencil", pygame.K_e: "eraser",
                       pygame.K_f: "fill", pygame.K_k: "picker",
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
            color = config.COLOR_SELECTED if active else config.COLOR_HOVER
            pygame.draw.rect(surf, color, btn_rect, border_radius=3)
            pygame.draw.rect(surf, config.COLOR_BORDER, btn_rect, 1, border_radius=3)
            text = self.font.render(f"{display}  [{shortcut}]", True, config.COLOR_TEXT)
            surf.blit(text, (x + 6, y + (BTN_H - text.get_height()) // 2))
            y += BTN_H + BTN_PAD
