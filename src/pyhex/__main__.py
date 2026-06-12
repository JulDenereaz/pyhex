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
        help="Hex circumradius in pixels (default %(default)s → %(default)s*2 × round(%(default)s*√3) bbox)",
    )
    args = parser.parse_args()

    pygame.init()
    try:
        app = Application(tileset_path=args.tileset, tile_size=args.tile_size)
        app.run()
    except Exception as exc:
        print(f"Fatal error: {exc}", file=sys.stderr)
        raise
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
