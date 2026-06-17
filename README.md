# pyhex

A small pygame-based pixel editor for painting hexagon-masked tiles inside a
square tileset image — handy for building hex tilesets (e.g. for Godot)
where each tile is a square PNG cell but only the hexagonal area should be
painted.

## Features

- **Tools**: Pencil (`P`), Eraser (`E`), Fill (`F`), Color Picker (`K`),
  Noise (`N`, with an adjustable variation slider)
- **Undo / redo**: `Ctrl+Z` / `Ctrl+Y`
- **Save**: `Ctrl+S` (also auto-saves on quit if there are unsaved changes)
- **Open tileset**: `Ctrl+O`, via a built-in file browser modal
- **Zoom**: `+` / `-`
- **Pan**: middle-mouse drag
- **PICO-8 32-color palette** built in
- **Tileset overview** grid showing every tile, with rulers and live
  coordinate display in the editor

## Requirements

- Python ≥ 3.12, **or** Docker
- A display: pyhex is a GUI app (pygame/SDL) and needs X11/Wayland. This
  works out of the box on Linux desktops and on WSL2 with WSLg.

## Quick start — Docker

No `make` required, just Docker:

```bash
docker compose up --build
```

That's it — Docker creates the bind-mounted `./assets` directory
automatically if it doesn't exist yet, and `xhost` is generally not needed
under WSLg.

If you're on native Linux and see an X11 error like `cannot open display`,
run this once on the host before starting the container:

```bash
xhost +local:docker
```

To stop and remove the container: `docker compose down`.

## Quick start — local

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pyhex
```

## CLI options

```
python -m pyhex [--tileset PATH] [--tile-size N]
```

- `--tileset PATH` — path to the tileset PNG (default `assets/tileset.png`,
  created blank if it doesn't exist)
- `--tile-size N` — tile pixel size, e.g. `--tile-size 32` → 32×32 px tiles
  (default `64`)

## Makefile (optional convenience)

If you have `make` installed, these shortcuts are also available:

| Target       | Description                              |
|--------------|-------------------------------------------|
| `make run`   | Build and run via Docker                  |
| `make dev`   | Run locally with `.venv` (faster dev loop)|
| `make test`  | Run the test suite                        |
| `make build` | Build the Docker image only               |
| `make clean` | Stop and remove Docker containers         |

## Tests

```bash
pytest tests/ -v
```

## License

MIT — see [LICENSE](LICENSE).
