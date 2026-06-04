SERVICE = service/auth_service

.PHONY: up down build dev test lint format migrate migration seed init-db docker-seed docker-init-db set-admin

up:
	docker compose up -d

build:
	docker compose up -d --build

down:
	docker compose down

dev:
	cd $(SERVICE) && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	cd $(SERVICE) && uv run pytest

lint:
	cd $(SERVICE) && uv run ruff check .

format:
	cd $(SERVICE) && uv run ruff format . && uv run ruff check --fix .

migrate:
	cd $(SERVICE) && uv run alembic upgrade head

migration:
	cd $(SERVICE) && uv run alembic revision --autogenerate -m "$(name)"

seed:
	cd $(SERVICE) && uv run python -m app.cli.seed

init-db:
	cd $(SERVICE) && uv run alembic upgrade head
	cd $(SERVICE) && uv run python -m app.cli.seed

# seed + create admin (prompts for email/password)
create-admin:
	cd $(SERVICE) && uv run python -m app.cli.seed --admin

# Docker variants
docker-seed:
	docker compose exec auth_service python -m app.cli.seed

docker-init-db:
	docker compose exec auth_service alembic upgrade head
	docker compose exec auth_service python -m app.cli.seed

docker-create-admin:
	docker compose exec auth_service python -m app.cli.seed --admin
