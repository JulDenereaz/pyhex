import numpy as np
import pytest
from pathlib import Path
from PIL import Image
from pyhex.tileset import Tileset


@pytest.fixture
def tmp_tileset(tmp_path):
    tw, th = 64, 55
    img = Image.new("RGBA", (tw * 4, th * 3), (0, 0, 0, 0))
    # Paint a distinctive pixel in tile (1, 2)
    img.putpixel((2 * tw + 10, 1 * th + 10), (255, 0, 128, 255))
    path = tmp_path / "tileset.png"
    img.save(path)
    return str(path), tw, th


def test_load_dimensions(tmp_tileset):
    path, tw, th = tmp_tileset
    ts = Tileset(path, tw, th)
    assert ts.cols == 4
    assert ts.rows == 3


def test_tile_shape(tmp_tileset):
    path, tw, th = tmp_tileset
    ts = Tileset(path, tw, th)
    tile = ts.get_tile(0, 0)
    assert tile.shape == (th, tw, 4)
    assert tile.dtype == np.uint8


def test_distinctive_pixel_preserved(tmp_tileset):
    path, tw, th = tmp_tileset
    ts = Tileset(path, tw, th)
    tile = ts.get_tile(1, 2)
    assert tuple(tile[10, 10]) == (255, 0, 128, 255)


def test_round_trip_save(tmp_tileset):
    path, tw, th = tmp_tileset
    ts = Tileset(path, tw, th)
    original = ts.get_tile(1, 2).copy()
    ts.save()

    ts2 = Tileset(path, tw, th)
    assert np.array_equal(ts2.get_tile(1, 2), original)


def test_set_tile_and_save(tmp_tileset):
    path, tw, th = tmp_tileset
    ts = Tileset(path, tw, th)
    new_tile = np.zeros((th, tw, 4), dtype=np.uint8)
    new_tile[5, 5] = (100, 150, 200, 255)
    ts.set_tile(0, 0, new_tile)
    ts.save()

    ts2 = Tileset(path, tw, th)
    assert tuple(ts2.get_tile(0, 0)[5, 5]) == (100, 150, 200, 255)


def test_missing_file_creates_blank(tmp_path):
    path = str(tmp_path / "new_tileset.png")
    ts = Tileset(path, 64, 55)
    assert Path(path).exists()
    assert ts.cols == 4
    assert ts.rows == 4
