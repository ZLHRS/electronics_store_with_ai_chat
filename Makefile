SERVICE = service/auth_service
USER_SERVICE = service/user_service
PRODUCT_SERVICE = service/product_service
CART_SERVICE = service/cart_service

.PHONY: up down build dev test lint format migrate migration seed init-db docker-seed docker-init-db set-admin \
        up-user build-user down-user \
        up-product build-product down-product \
        up-cart build-cart down-cart \
        user-dev user-test user-lint user-format user-migrate user-migration \
        product-dev product-test product-lint product-format product-migrate product-migration \
        cart-dev cart-test cart-lint cart-format cart-migrate cart-migration

up:
	docker compose up -d

build:
	docker compose up -d --build

down:
	docker compose down

up-user:
	docker compose up -d user_service

build-user:
	docker compose up -d --build user_service

down-user:
	docker compose stop user_service

up-product:
	docker compose up -d product_service

build-product:
	docker compose up -d --build product_service

down-product:
	docker compose stop product_service

up-cart:
	docker compose up -d cart_service

build-cart:
	docker compose up -d --build cart_service

down-cart:
	docker compose stop cart_service

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

# User service
user-dev:
	cd $(USER_SERVICE) && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001

user-test:
	cd $(USER_SERVICE) && uv run pytest

user-lint:
	cd $(USER_SERVICE) && uv run ruff check .

user-format:
	cd $(USER_SERVICE) && uv run ruff format . && uv run ruff check --fix .

user-migrate:
	cd $(USER_SERVICE) && uv run alembic upgrade head

user-migration:
	cd $(USER_SERVICE) && uv run alembic revision --autogenerate -m "$(name)"

# Product service
product-dev:
	cd $(PRODUCT_SERVICE) && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8002

product-test:
	cd $(PRODUCT_SERVICE) && uv run pytest

product-lint:
	cd $(PRODUCT_SERVICE) && uv run ruff check .

product-format:
	cd $(PRODUCT_SERVICE) && uv run ruff format . && uv run ruff check --fix .

product-migrate:
	cd $(PRODUCT_SERVICE) && uv run alembic upgrade head

product-migration:
	cd $(PRODUCT_SERVICE) && uv run alembic revision --autogenerate -m "$(name)"

# Cart service
cart-dev:
	cd $(CART_SERVICE) && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8003

cart-test:
	cd $(CART_SERVICE) && uv run pytest

cart-lint:
	cd $(CART_SERVICE) && uv run ruff check .

cart-format:
	cd $(CART_SERVICE) && uv run ruff format . && uv run ruff check --fix .

cart-migrate:
	cd $(CART_SERVICE) && uv run alembic upgrade head

cart-migration:
	cd $(CART_SERVICE) && uv run alembic revision --autogenerate -m "$(name)"
