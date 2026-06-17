# Changelog

## v0.1.0 — 2026-06-17

Initial usable release.

### Added
- Hexagonal tileset pixel editor built with pygame: paint a hex-masked
  area inside square tile cells of a PNG tileset.
- Editing tools: Pencil, Eraser, Fill, Color Picker, and Noise (with
  adjustable variation slider).
- Undo/redo, save (manual and on-quit auto-save), and tileset open via a
  built-in file browser modal.
- Tile editor with zoom, middle-mouse pan, pixel rulers, and live
  coordinate display.
- Tileset overview grid showing all tiles.
- Built-in PICO-8 32-color palette.
- `--tile-size` CLI option to control tile pixel dimensions.
- Docker support (`docker-compose.yml`, `docker/Dockerfile`) for running
  via X11/WSLg without a local Python setup.
- Test suite covering hex geometry and tileset load/save round-trips.
- README, MIT LICENSE, `.dockerignore`.
