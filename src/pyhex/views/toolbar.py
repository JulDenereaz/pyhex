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
    def __init__(self, state: AppState, font: pygame.font.Font,
                 on_open: "callable | None" = None,
                 on_add_row: "callable | None" = None,
                 on_add_col: "callable | None" = None):
        self.state       = state
        self.font        = font
        self._on_open    = on_open
        self._on_add_row = on_add_row
        self._on_add_col = on_add_col
        self._rects: dict[str, pygame.Rect] = {}
        self._open_rect     = pygame.Rect(0, 0, 0, 0)
        self._add_row_rect  = pygame.Rect(0, 0, 0, 0)
        self._add_col_rect  = pygame.Rect(0, 0, 0, 0)
        self._slider_rect   = pygame.Rect(0, 0, 0, 0)
        self._dragging_slider = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        # ---- open / expand buttons ----
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._open_rect.collidepoint(event.pos):
                if self._on_open:
                    self._on_open()
                return True
            if self._add_row_rect.collidepoint(event.pos):
                if self._on_add_row:
                    self._on_add_row()
                return True
            if self._add_col_rect.collidepoint(event.pos):
                if self._on_add_col:
                    self._on_add_col()
                return True

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

        btn_w = rect.width - BTN_PAD * 2

        # Open file button (top)
        open_rect = pygame.Rect(x, y, btn_w, BTN_H)
        self._open_rect = open_rect
        pygame.draw.rect(surf, (55, 80, 55), open_rect, border_radius=3)
        pygame.draw.rect(surf, config.COLOR_BORDER, open_rect, 1, border_radius=3)
        open_lbl = self.font.render("Open tileset...  [Ctrl+O]", True, config.COLOR_TEXT)
        surf.blit(open_lbl, (x + 6, y + (BTN_H - open_lbl.get_height()) // 2))
        y += BTN_H + BTN_PAD * 2

        label = self.font.render("Tools", True, config.COLOR_TEXT)
        surf.blit(label, (x, y))
        y += label.get_height() + BTN_PAD

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

        # Expand tileset buttons
        y += BTN_PAD * 2
        exp_label = self.font.render("Tileset", True, config.COLOR_TEXT)
        surf.blit(exp_label, (x, y))
        y += exp_label.get_height() + BTN_PAD

        half_w = (btn_w - BTN_PAD) // 2
        row_rect = pygame.Rect(x, y, half_w, BTN_H)
        col_rect = pygame.Rect(x + half_w + BTN_PAD, y, btn_w - half_w - BTN_PAD, BTN_H)
        self._add_row_rect = row_rect
        self._add_col_rect = col_rect
        for r, label in ((row_rect, "+ Row"), (col_rect, "+ Col")):
            pygame.draw.rect(surf, (55, 55, 80), r, border_radius=3)
            pygame.draw.rect(surf, config.COLOR_BORDER, r, 1, border_radius=3)
            lbl = self.font.render(label, True, config.COLOR_TEXT)
            surf.blit(lbl, (r.x + (r.width - lbl.get_width()) // 2,
                            r.y + (BTN_H - lbl.get_height()) // 2))
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
