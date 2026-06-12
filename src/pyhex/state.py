from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np


@dataclass
class AppState:
    tileset: object = None          # Tileset | None
    tile_w: int = 64
    tile_h: int = 55

    selected_tile: tuple[int, int] = (0, 0)
    active_tile_data: np.ndarray | None = None  # working copy (RGBA uint8)

    active_tool: str = "pencil"     # pencil | eraser | fill | picker
    foreground_color: tuple[int, int, int, int] = (255, 255, 255, 255)
    zoom: int = 8
    editor_offset: list[int] = field(default_factory=lambda: [0, 0])  # pan offset px

    dirty: bool = False             # unsaved changes to active tile
    noise_variation: int = 30      # ±channel variation for noise tool (1–100)
    _undo_stack: list = field(default_factory=list, repr=False)
    _redo_stack: list = field(default_factory=list, repr=False)

    def push_undo(self) -> None:
        if self.active_tile_data is None:
            return
        self._undo_stack.append(self.active_tile_data.copy())
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> None:
        if not self._undo_stack:
            return
        self._redo_stack.append(self.active_tile_data.copy())
        self.active_tile_data = self._undo_stack.pop()
        self.dirty = True

    def redo(self) -> None:
        if not self._redo_stack:
            return
        self._undo_stack.append(self.active_tile_data.copy())
        self.active_tile_data = self._redo_stack.pop()
        self.dirty = True

    def select_tile(self, row: int, col: int) -> None:
        if self.dirty:
            self._commit_tile()
        self.selected_tile = (row, col)
        if self.tileset is not None:
            self.active_tile_data = self.tileset.get_tile(row, col).copy()
        self.dirty = False
        self.editor_offset = [0, 0]
        self._undo_stack.clear()
        self._redo_stack.clear()

    def _commit_tile(self) -> None:
        if self.tileset is not None and self.active_tile_data is not None:
            r, c = self.selected_tile
            self.tileset.set_tile(r, c, self.active_tile_data)

    def save(self, mask=None) -> None:
        self._commit_tile()
        if self.tileset is not None:
            self.tileset.save(mask=mask)
        self.dirty = False
