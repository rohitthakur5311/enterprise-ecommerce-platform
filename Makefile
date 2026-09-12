.PHONY: install test lint security run docker

install:
	pip install -r requirements.txt

test:
	pytest -q --cov=services --cov-report=term-missing --cov-fail-under=85

lint:
	ruff check .

security:
	bandit -r services
	pip-audit -r requirements.txt

run:
	uvicorn services.gateway.app:app --reload --port 8000

docker:
	docker compose up --build
