.PHONY: dev migrate seed test lint docker-build docker-up docker-down clean

# Development
dev:
	uv run python manage.py runserver

migrate:
	uv run python manage.py migrate

seed:
	uv run python manage.py seed_data

shell:
	uv run python manage.py shell

# Testing & Quality
test:
	uv run pytest -v

check:
	uv run python manage.py check

# Docker
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f web

# Setup
install:
	uv sync --dev

setup: install migrate seed
	@echo "Ready! Run 'make dev' to start the server."

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage staticfiles
