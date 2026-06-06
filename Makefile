VENV := .venv
PYTHON := $(VENV)/bin/python
UV := uv

.PHONY: venv install run run-local rag-ingest test docker-build run-docker run-docker-bg docker-logs docker-down

venv:
	@test -d $(VENV) || $(UV) venv --python 3.12 $(VENV)

install: venv
	$(UV) sync

run: venv
	$(PYTHON) -m src.main

run-local: run

rag-ingest: venv
	$(PYTHON) -m src.rag.index_pdf

test: venv
	$(PYTHON) -m unittest discover -s tests

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
