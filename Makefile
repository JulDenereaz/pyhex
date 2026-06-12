.PHONY: run dev test build clean

# Run inside Docker (requires WSLg / X11)
run:
	@mkdir -p assets
	@xhost +local:docker 2>/dev/null || true
	docker compose up --build

# Run locally (faster for development)
dev:
	@mkdir -p assets
	.venv/bin/python -m pyhex

# Run tests
test:
	.venv/bin/pytest tests/ -v

# Build Docker image without starting
build:
	docker compose build

# Stop and remove containers
clean:
	docker compose down
