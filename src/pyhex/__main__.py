import argparse
import sys
import pygame
from pyhex.app import Application
from pyhex import config


def main() -> None:
    parser = argparse.ArgumentParser(description="pyhex — Hexagonal tileset pixel editor")
    parser.add_argument(
        "--tileset",
        default="assets/tileset.png",
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
