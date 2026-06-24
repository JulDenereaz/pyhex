import argparse
import sys
from pathlib import Path
import pygame
from pyhex.app import Application
from pyhex import config

_DEFAULT_TILESET = "assets/tileset.png"


def main() -> None:
    parser = argparse.ArgumentParser(description="pyhex — Hexagonal tileset pixel editor")
    parser.add_argument(
        "--tileset",
        default=_DEFAULT_TILESET,
        help="Path to the tileset PNG (created blank if absent)",
    )
    parser.add_argument(
        "--tile-size",
        type=int,
        default=config.DEFAULT_TILE_SIZE,
        metavar="S",
        help="Tile pixel size: --tile-size 32 → 32×32 tile, --tile-size 64 → 64×64 tile (default %(default)s)",
    )
    args = parser.parse_args()

    # Auto-suffix the default path with the tile size so different resolutions
    # stay in separate files (e.g. tileset_32.png, tileset_64.png).
    if args.tileset == _DEFAULT_TILESET:
        p = Path(args.tileset)
        args.tileset = str(p.parent / f"{p.stem}_{args.tile_size}{p.suffix}")

    pygame.display.init()
    pygame.font.init()
    try:
        app = Application(tileset_path=args.tileset, tile_size=args.tile_size)
        app.run()
    except Exception as exc:
        print(f"Fatal error: {exc}", file=sys.stderr)
        raise
    finally:
        pygame.font.quit()
        pygame.display.quit()


if __name__ == "__main__":
    main()
