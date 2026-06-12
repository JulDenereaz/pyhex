from math import sqrt
import numpy as np
import pytest
from pyhex.hex_geometry import hex_tile_size, make_hex_mask, hex_polygon_points


def test_tile_size_dimensions():
    w, h = hex_tile_size(32)
    assert w == 64   # square tiles: 2 * circumradius
    assert h == 64


def test_mask_shape():
    w, h = hex_tile_size(32)
    mask = make_hex_mask(w, h)
    assert mask.shape == (h, w)
    assert mask.dtype == bool


def test_center_pixel_inside():
    w, h = hex_tile_size(32)
    mask = make_hex_mask(w, h)
    assert mask[h // 2, w // 2], "center pixel should be inside the hex"


def test_corner_pixels_outside():
    w, h = hex_tile_size(32)
    mask = make_hex_mask(w, h)
    # All four corners of the bounding box are outside a pointy-top hex
    assert not mask[0, 0], "top-left corner should be outside the hex"
    assert not mask[0, w - 1], "top-right corner should be outside the hex"
    assert not mask[h - 1, 0], "bottom-left corner should be outside the hex"
    assert not mask[h - 1, w - 1], "bottom-right corner should be outside the hex"


def test_mask_has_inside_pixels():
    w, h = hex_tile_size(32)
    mask = make_hex_mask(w, h)
    assert mask.any(), "mask should have at least one True pixel"


def test_mask_has_outside_pixels():
    w, h = hex_tile_size(32)
    mask = make_hex_mask(w, h)
    assert not mask.all(), "mask should have at least one False pixel (corners)"


def test_hex_polygon_six_vertices():
    w, h = hex_tile_size(32)
    pts = hex_polygon_points(w, h)
    assert len(pts) == 6


@pytest.mark.parametrize("size", [16, 32, 48, 64])
def test_mask_symmetry(size):
    w, h = hex_tile_size(size)
    mask = make_hex_mask(w, h)
    # Left-right symmetry
    assert np.array_equal(mask, mask[:, ::-1])
    # Top-bottom symmetry
    assert np.array_equal(mask, mask[::-1, :])
