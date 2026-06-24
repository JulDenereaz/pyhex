from pathlib import Path
import numpy as np
from PIL import Image


class Tileset:
    def __init__(self, path: str, tile_w: int, tile_h: int):
        self.path = Path(path)
        self.tile_w = tile_w
        self.tile_h = tile_h
        self._load()

    def _load(self):
        if self.path.exists():
            img = Image.open(self.path).convert("RGBA")
        else:
            # Create a blank 4-tile-wide, 4-tile-tall tileset
            img = Image.new("RGBA", (self.tile_w * 4, self.tile_h * 4), (0, 0, 0, 0))
            self.path.parent.mkdir(parents=True, exist_ok=True)
            img.save(self.path)

        self.cols = max(1, img.width // self.tile_w)
        self.rows = max(1, img.height // self.tile_h)
        arr = np.array(img, dtype=np.uint8)
        self.tiles: list[list[np.ndarray]] = [
            [
                arr[
                    r * self.tile_h : (r + 1) * self.tile_h,
                    c * self.tile_w : (c + 1) * self.tile_w,
                ].copy()
                for c in range(self.cols)
            ]
            for r in range(self.rows)
        ]

    def get_tile(self, row: int, col: int) -> np.ndarray:
        return self.tiles[row][col]

    def set_tile(self, row: int, col: int, data: np.ndarray) -> None:
        self.tiles[row][col] = data.copy()

    def save(self, mask: "np.ndarray | None" = None) -> None:
        h = self.rows * self.tile_h
        w = self.cols * self.tile_w
        arr = np.zeros((h, w, 4), dtype=np.uint8)
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c].copy()
                if mask is not None:
                    tile[~mask, 3] = 0   # zero alpha outside hex on disk
                arr[
                    r * self.tile_h : (r + 1) * self.tile_h,
                    c * self.tile_w : (c + 1) * self.tile_w,
                ] = tile
        Image.fromarray(arr, "RGBA").save(self.path)

    def add_row(self) -> None:
        blank = np.zeros((self.tile_h, self.tile_w, 4), dtype=np.uint8)
        self.tiles.append([blank.copy() for _ in range(self.cols)])
        self.rows += 1

    def add_col(self) -> None:
        blank = np.zeros((self.tile_h, self.tile_w, 4), dtype=np.uint8)
        for row in self.tiles:
            row.append(blank.copy())
        self.cols += 1

    def reload(self) -> None:
        self._load()
