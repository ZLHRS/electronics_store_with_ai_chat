# Auth Service

JWT-аутентификация с refresh-токенами, управлением сессиями и защитой от token reuse.

## Стек

- **FastAPI** + **SQLAlchemy** (async) + **Dishka** (DI)
- **PostgreSQL** — хранение пользователей и сессий
- **Redis** — rate limiting
- **Alembic** — миграции

## Быстрый старт

### Docker (рекомендуется)

```bash
cp .env.example .env   # заполнить секреты
make build             # поднять все сервисы
make migrate           # применить миграции
```

### Локально

```bash
cp .env.example .env
uv sync
make migrate
make dev
```

## Команды

| Команда                        | Описание                        |
|--------------------------------|---------------------------------|
| `make build`                   | Поднять сервисы и пересобрать   |
| `make up`                      | Поднять сервисы                 |
| `make down`                    | Остановить сервисы              |
| `make dev`                     | Локальный сервер с hot-reload   |
| `make test`                    | Запустить тесты                 |
| `make lint`                    | Проверить линтером              |
| `make format`                  | Отформатировать код             |
| `make migrate`                 | Применить миграции              |
| `make migration name=<имя>`    | Создать новую миграцию          |

## API

| Метод  | Endpoint               | Описание                     |
|--------|------------------------|------------------------------|
| POST   | `/api/v1/register`     | Регистрация                  |
| POST   | `/api/v1/login`        | Вход, установка cookie       |
| POST   | `/api/v1/refresh`      | Обновление токенов           |
| GET    | `/api/v1/me`           | Текущий пользователь         |
| POST   | `/api/v1/logout`       | Выход из текущей сессии      |
| POST   | `/api/v1/logout/all`   | Выход из всех сессий         |
| GET    | `/api/v1/health_check` | Статус сервиса + БД          |

## Структура

```
app/
├── application/        # бизнес-логика (сервисы, DTO)
├── domain/             # сущности, протоколы репозиториев, исключения
├── infrastructure/     # БД, репозитории, DI, security
└── presentation/       # роутеры, схемы, exception handlers
```

## Переменные окружения

Все переменные описаны в `.env.example`.
Секреты, которые обязательно менять перед деплоем: `AUTH_SECRET_KEY`, `DB_PASSWORD`.
