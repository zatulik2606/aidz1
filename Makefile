install:
	uv sync

run:
	uv run python -m src.main

docker-build:
	docker build -t aidz1-bot .

run-docker:
	docker run --rm --env-file .env aidz1-bot

docker-down:
	@echo "No persistent docker service to stop for run-docker"
