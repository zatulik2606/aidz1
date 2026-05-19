.PHONY: install run run-local docker-build run-docker run-docker-bg docker-logs docker-down

install:
	uv sync

run:
	uv run python -m src.main

run-local: run

docker-build:
	docker compose build

run-docker:
	docker compose up --build bot

run-docker-bg:
	docker compose up -d --build bot

docker-logs:
	docker compose logs -f bot

docker-down:
	docker compose down
