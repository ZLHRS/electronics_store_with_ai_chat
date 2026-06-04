# Auth Service

Сервис аутентификации для интернет-магазина с AI-ассистентом.

JWT + refresh token rotation, RBAC через Redis, одна активная сессия на пользователя.

## Стек

- **FastAPI** + **SQLAlchemy async** + **Dishka** (DI)
- **PostgreSQL** — пользователи, сессии, роли, пермишены
- **Redis** — кеш пермишенов (быстрая проверка прав без запроса в БД)
- **Alembic** — миграции схемы

## Быстрый старт

### Docker

```bash
cp .env.example .env        # заполнить DB_PASSWORD, AUTH_SECRET_KEY, REDIS_URL
make build                  # собрать и поднять все сервисы
# миграции + seed применяются автоматически при старте контейнера
make docker-create-admin    # создать первого администратора
```

### Локально

```bash
cp .env.example .env
uv sync
make init-db                # migrate + seed
make dev
```

## Команды

| Команда | Описание |
|---------|----------|
| `make build` | Пересобрать и поднять Docker |
| `make up` / `make down` | Поднять / остановить |
| `make dev` | Локальный сервер с hot-reload |
| `make test` | Тесты (отдельная БД `mydb_test`) |
| `make lint` / `make format` | Линтер / форматирование |
| `make migrate` | Применить миграции (локально) |
| `make migration name=X` | Создать новую миграцию |
| `make init-db` | migrate + seed (локально) |
| `make seed` | Только seed ролей/пермишенов |
| `make create-admin` | Создать администратора |
| `make docker-init-db` | migrate + seed в Docker |
| `make docker-create-admin` | Создать администратора в Docker |

## API

| Метод | Endpoint | Доступ | Описание |
|-------|----------|--------|----------|
| POST | `/api/v1/register` | Публичный | Регистрация (автоматически роль `user`) |
| POST | `/api/v1/login` | Публичный | Вход, устанавливает httponly cookies |
| POST | `/api/v1/refresh` | Публичный | Обновление токенов |
| GET | `/api/v1/me` | Авторизованный | Профиль + роли текущего пользователя |
| POST | `/api/v1/logout` | Авторизованный | Выход из текущей сессии |
| POST | `/api/v1/logout/all` | Только admin | Выход из всех сессий |
| GET | `/api/v1/health_check` | Публичный | Статус сервиса |

Токены передаются через httponly cookies: `access_token` и `refresh_token`.

## RBAC

```
users → user_roles → roles → role_permissions → permissions
```

Пермишены кешируются в Redis при логине. При logout кеш удаляется — доступ закрывается мгновенно.

**Роли по умолчанию:**

| Роль | Пермишены |
|------|-----------|
| `user` | `users.read`, `products.read`, `orders.read.own`, `orders.update.own` |
| `manager` | products + orders (включая all) |
| `admin` | Все пермишены |

**Добавить пермишен в роут:**
```python
from app.domain.permissions import P
from app.presentation.deps import require_permission

@router.delete("/users/{id}", dependencies=[Depends(require_permission(P.USERS_DELETE))])
async def delete_user(user_id: UUID):
    ...
```

**Policy check (own vs all):**
```python
if item.user_id != user.id and not user.has_permission(P.ORDERS_READ_ALL):
    raise HTTPException(403)
```

## Безопасность

- Одна активная сессия на пользователя
- Refresh token rotation — токен одноразовый, после использования ревокается
- Reuse detection — повторное использование старого токена отзывает все сессии пользователя
- Logout инвалидирует access token через удаление из Redis (не ждёт истечения TTL)
- Rate limiting на `/login`, `/register`, `/refresh`

## Структура

```
app/
├── factory.py              # create_app()
├── config.py               # конфиг через pydantic-settings
├── exceptions.py           # доменные исключения
├── domain/
│   ├── entity/             # UserEntity, SessionEntity (dataclasses)
│   ├── repo/               # Protocol-интерфейсы репозиториев
│   └── permissions.py      # class P: константы пермишенов
├── application/
│   ├── dto/                # команды и результаты
│   └── service/
│       └── auth_service.py # вся бизнес-логика
├── infrastructure/
│   ├── cache/              # PermissionCache (Redis)
│   ├── db/                 # модели, репозитории
│   ├── di/                 # Dishka провайдеры
│   ├── mapper/             # model → entity
│   └── security.py         # JWT, bcrypt
├── presentation/
│   ├── api/                # роуты
│   ├── deps.py             # CurrentUser, require_permission
│   └── exception.py        # обработчики ошибок
└── cli/
    └── seed.py             # seed ролей и пермишенов
```

## Переменные окружения

Все переменные описаны в `.env.example`.

Обязательно менять перед деплоем: `AUTH_SECRET_KEY`, `DB_PASSWORD`.

Сгенерировать секрет:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
