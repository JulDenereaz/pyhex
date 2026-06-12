from __future__ import annotations
import os
from pathlib import Path
import pygame
from pyhex import config

MODAL_W   = 540
MODAL_H   = 380
HEADER_H  = 48
FOOTER_H  = 52
LIST_H    = MODAL_H - HEADER_H - FOOTER_H
ROW_H     = 22
PADDING   = 10

_MUTED     = (120, 120, 120)
_DIR_COLOR = (140, 190, 255)


class FileBrowser:
    """Modal pygame file picker — shows only folders and .png files."""

    def __init__(self, start_path: str = "."):
        path = Path(start_path).resolve()
        self._path    = path if path.is_dir() else path.parent
        self._entries: list[tuple[bool, str]] = []   # (is_dir, name)
        self._selected = -1
        self._scroll   = 0
        self._result:  str | None = None
        self._cancelled = False
        self._font     = pygame.font.SysFont(None, 18)
        self._big_font = pygame.font.SysFont(None, 20)
        self._refresh()

    # ------------------------------------------------------------------
    @property
    def done(self) -> bool:
        return self._result is not None or self._cancelled

    @property
    def result(self) -> str | None:
        return self._result

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event,
                     screen_size: tuple[int, int]) -> None:
        modal = self._modal_rect(screen_size)
        list_rect = pygame.Rect(modal.x + PADDING, modal.y + HEADER_H,
                                modal.width - PADDING * 2, LIST_H)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._cancelled = True
            elif event.key == pygame.K_RETURN:
                self._activate_selected()
            elif event.key == pygame.K_UP:
                self._selected = max(0, self._selected - 1)
                self._ensure_visible()
            elif event.key == pygame.K_DOWN:
                self._selected = min(len(self._entries) - 1, self._selected + 1)
                self._ensure_visible()
            elif event.key == pygame.K_BACKSPACE:
                self._go_up()
            return

        if event.type == pygame.MOUSEWHEEL:
            if list_rect.collidepoint(pygame.mouse.get_pos()):
                max_scroll = max(0, len(self._entries) - LIST_H // ROW_H)
                self._scroll = max(0, min(max_scroll, self._scroll - event.y))
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Cancel / Open buttons
            cancel_r, open_r = self._button_rects(modal)
            if cancel_r.collidepoint(event.pos):
                self._cancelled = True
                return
            if open_r.collidepoint(event.pos):
                self._confirm()
                return

            # "Go up" arrow
            up_r = pygame.Rect(modal.right - PADDING - 24,
                               modal.y + PADDING, 24, 20)
            if up_r.collidepoint(event.pos):
                self._go_up()
                return

            # Entry row
            if list_rect.collidepoint(event.pos):
                row = (event.pos[1] - list_rect.y) // ROW_H + self._scroll
                if 0 <= row < len(self._entries):
                    if row == self._selected:
                        self._activate_selected()   # double-click effect
                    else:
                        self._selected = row

    def draw(self, surf: pygame.Surface) -> None:
        sw, sh = surf.get_size()
        modal   = self._modal_rect((sw, sh))

        # Dim background
        dim = pygame.Surface((sw, sh), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        surf.blit(dim, (0, 0))

        # Modal box
        pygame.draw.rect(surf, config.COLOR_PANEL,  modal, border_radius=6)
        pygame.draw.rect(surf, config.COLOR_BORDER, modal, 1, border_radius=6)

        # Title
        title = self._big_font.render("Open Tileset", True, config.COLOR_TEXT)
        surf.blit(title, (modal.x + PADDING, modal.y + PADDING))

        # Current path + ↑ button
        path_str = str(self._path)
        if len(path_str) > 58:
            path_str = "…" + path_str[-57:]
        plbl = self._font.render(path_str, True, _MUTED)
        surf.blit(plbl, (modal.x + PADDING, modal.y + PADDING + 20))

        up_r = pygame.Rect(modal.right - PADDING - 24, modal.y + PADDING, 24, 20)
        pygame.draw.rect(surf, config.COLOR_HOVER, up_r, border_radius=3)
        pygame.draw.rect(surf, config.COLOR_BORDER, up_r, 1, border_radius=3)
        up_lbl = self._font.render("↑", True, config.COLOR_TEXT)
        surf.blit(up_lbl, (up_r.centerx - up_lbl.get_width() // 2,
                           up_r.centery - up_lbl.get_height() // 2))

        # Separator
        pygame.draw.line(surf, config.COLOR_BORDER,
                         (modal.x, modal.y + HEADER_H - 1),
                         (modal.right, modal.y + HEADER_H - 1))

        # Entry list
        list_rect = pygame.Rect(modal.x + PADDING, modal.y + HEADER_H,
                                modal.width - PADDING * 2, LIST_H)
        old_clip = surf.get_clip()
        surf.set_clip(list_rect)

        visible = LIST_H // ROW_H + 1
        for i in range(visible):
            idx = i + self._scroll
            if idx >= len(self._entries):
                break
            is_dir, name = self._entries[idx]
            row_r = pygame.Rect(list_rect.x,
                                list_rect.y + i * ROW_H,
                                list_rect.width, ROW_H)
            if idx == self._selected:
                pygame.draw.rect(surf, config.COLOR_SELECTED, row_r, border_radius=3)
            prefix = "▶ " if is_dir else "  "
            color  = _DIR_COLOR if is_dir else config.COLOR_TEXT
            lbl = self._font.render(prefix + name, True, color)
            surf.blit(lbl, (row_r.x + 4,
                            row_r.y + (ROW_H - lbl.get_height()) // 2))

        surf.set_clip(old_clip)

        # Footer separator
        pygame.draw.line(surf, config.COLOR_BORDER,
                         (modal.x, modal.bottom - FOOTER_H),
                         (modal.right, modal.bottom - FOOTER_H))

        # Selected file preview
        if 0 <= self._selected < len(self._entries):
            is_dir, name = self._entries[self._selected]
            if not is_dir:
                prev = self._font.render(
                    str(self._path / name), True, _MUTED)
                surf.blit(prev, (modal.x + PADDING,
                                 modal.bottom - FOOTER_H + 6))

        # Cancel / Open buttons
        cancel_r, open_r = self._button_rects(modal)
        can_open = (0 <= self._selected < len(self._entries)
                    and not self._entries[self._selected][0])

        for r, label, active in ((cancel_r, "Cancel", False),
                                  (open_r,   "Open",   can_open)):
            color = config.COLOR_SELECTED if active else config.COLOR_HOVER
            pygame.draw.rect(surf, color,               r, border_radius=4)
            pygame.draw.rect(surf, config.COLOR_BORDER, r, 1, border_radius=4)
            lbl = self._big_font.render(label, True, config.COLOR_TEXT)
            surf.blit(lbl, (r.centerx - lbl.get_width() // 2,
                            r.centery - lbl.get_height() // 2))

    # ------------------------------------------------------------------
    def _modal_rect(self, screen_size: tuple[int, int]) -> pygame.Rect:
        sw, sh = screen_size
        return pygame.Rect((sw - MODAL_W) // 2, (sh - MODAL_H) // 2,
                           MODAL_W, MODAL_H)

    def _button_rects(self, modal: pygame.Rect
                      ) -> tuple[pygame.Rect, pygame.Rect]:
        btn_y = modal.bottom - FOOTER_H + 14
        cancel = pygame.Rect(modal.x + PADDING,          btn_y, 90, 26)
        open_  = pygame.Rect(modal.right - PADDING - 90, btn_y, 90, 26)
        return cancel, open_

    def _refresh(self) -> None:
        try:
            items = sorted(os.listdir(self._path),
                           key=lambda n: n.lower())
        except PermissionError:
            items = []
        dirs  = [n for n in items
                 if (self._path / n).is_dir() and not n.startswith('.')]
        files = [n for n in items
                 if (self._path / n).is_file()
                 and n.lower().endswith('.png')]
        self._entries  = [(True, d) for d in dirs] + [(False, f) for f in files]
        self._selected = -1
        self._scroll   = 0

    def _go_up(self) -> None:
        parent = self._path.parent
        if parent != self._path:
            self._path = parent
            self._refresh()

    def _activate_selected(self) -> None:
        if not (0 <= self._selected < len(self._entries)):
            return
        is_dir, name = self._entries[self._selected]
        if is_dir:
            self._path = self._path / name
            self._refresh()
        else:
            self._confirm()

    def _confirm(self) -> None:
        if not (0 <= self._selected < len(self._entries)):
            return
        is_dir, name = self._entries[self._selected]
        if not is_dir:
            self._result = str(self._path / name)

    def _ensure_visible(self) -> None:
        visible = LIST_H // ROW_H
        if self._selected < self._scroll:
            self._scroll = self._selected
        elif self._selected >= self._scroll + visible:
            self._scroll = self._selected - visible + 1
