install:
	uv sync

run:
	uv run python -m src.main

docker-build:
	docker compose build

run-docker:
	docker compose up bot

docker-down:
	docker compose down
