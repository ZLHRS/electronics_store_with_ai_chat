# CLAUDE.md — Shop

## Инструкции для Claude

- Никогда не предлагай сделать коммит. Вместо этого — в конце задачи предложи готовое название коммита в формате Conventional Commits: `feat: ...`, `fix: ...`, `refactor: ...`, `chore: ...` и т.д.
- Не писать комментарии в коде. Никаких `# ...` или `"""..."""` пояснений — код должен быть самодокументируемым через названия.
- Всегда отвечать на русском языке.

---

## Контекст проекта

**Shop** — интернет-магазин с AI-ассистентом.

Монорепозиторий с микросервисами:
```
Shop/
├── service/auth_service/   # сервис аутентификации (текущий)
├── nginx/                  # reverse proxy
├── docker-compose.yml
└── Makefile
```



---

## Структура проекта

```
Shop/
├── docker-compose.yml          # postgres, redis, auth_service, nginx
├── .env                        # Docker-уровень: DB_HOST=postgres, REDIS_URL=redis://redis:6379
├── Makefile                    # команды (см. ниже)
└── service/
    └── auth_service/
        ├── main.py             # точка входа uvicorn: from app.factory import create_app; app = create_app()
        ├── app/
        │   ├── factory.py      # create_app() — FastAPI + Dishka + middleware + lifespan
        │   ├── config.py       # setup_config() читает .env через pydantic-settings
        │   ├── exceptions.py   # все доменные исключения
        │   ├── domain/
        │   │   ├── entity/     # UserEntity, SessionEntity (dataclasses, без ORM)
        │   │   ├── repo/       # Protocol-интерфейсы репозиториев
        │   │   └── permissions.py  # class P: USERS_READ = "users.read" ...
        │   ├── application/
        │   │   ├── dto/        # RegisterCommand, LoginTokens, UserResult ...
        │   │   └── service/
        │   │       └── auth_service.py  # вся бизнес-логика auth
        │   ├── infrastructure/
        │   │   ├── cache/
        │   │   │   └── permission_cache.py  # Redis: "permissions:user:{id}" → frozenset[str]
        │   │   ├── db/
        │   │   │   ├── model/  # SQLAlchemy модели (UserModel, RoleModel, PermissionModel ...)
        │   │   │   └── repo/   # SQLAlchemy реализации репозиториев
        │   │   ├── di/         # Dishka провайдеры (DBProvider, RedisProvider, AuthProvider)
        │   │   ├── mapper/     # model → entity конвертеры
        │   │   └── security.py # JWT encode/decode, bcrypt, SecurityService
        │   ├── presentation/
        │   │   ├── api/
        │   │   │   └── auth_api.py  # FastAPI роуты
        │   │   ├── deps.py     # CurrentUser, get_current_user, require_permission()
        │   │   └── exception.py # exception handlers
        │   └── cli/
        │       └── seed.py     # идемпотентный seed ролей и пермишенов
        ├── alembic/
        │   ├── env.py          # ВАЖНО: импортирует все модели для autogenerate
        │   └── versions/       # миграции — только схема, без данных
        └── tests/
            ├── conftest.py     # engine, app, client, db_session фикстуры
            ├── unit/           # FakeRepo, FakeCache — без БД
            ├── integration/    # реальная БД через db_session
            ├── api/            # httpx ASGITransport
            └── e2e/            # полный flow через httpx
```

## Ключевые архитектурные решения

### Auth flow
- **Access token**: JWT `{sub: user_id, exp, type: "access"}` — без роли, без пермишенов
- **Refresh token**: JWT + `jti: uuid4()` (уникален, защита от коллизий)
- **Одна сессия**: при логине проверяется `has_active_session(user_id)` → 409 если уже залогинен
- **Reuse detection**: refresh токен сразу ревокается после использования; повторное использование → отзыв всех сессий

### RBAC
```
users → user_roles → roles → role_permissions → permissions
```
- При регистрации: автоматически назначается роль `user`
- При логине: пермишены из БД → Redis `permissions:user:{id}` с TTL = access token expire
- На каждый запрос: GET из Redis (~1ms) + проверка строки
- При logout: Redis ключ удаляется → мгновенная инвалидация

### Добавить новый пермишен
1. `app/domain/permissions.py` — добавить константу в класс `P`
2. Новая миграция или обновить seed
3. В роуте: `dependencies=[Depends(require_permission(P.NEW_PERM))]`

### Добавить новую роль
1. Только в `app/cli/seed.py` → `ROLE_PERMISSIONS["new_role"] = [...]`
2. `make seed` (или `make docker-seed`)

## Провайдеры Dishka (DI)

| Scope | Провайдер | Что создаёт |
|-------|-----------|-------------|
| APP   | ConfigProvider | Config |
| APP   | DBProvider | AsyncEngine, async_sessionmaker |
| APP   | RedisProvider | redis.Redis, PermissionCache |
| APP   | AuthProvider | AuthConfig, SecurityService |
| REQUEST | DBProvider | AsyncSession |
| REQUEST | AuthProvider | UserRepo, SessionRepo, PermissionRepo, AuthService |

Сессия: `provide_session` в `db_di.py` — commit при успехе, rollback при ошибке.  
**Важно**: после `IntegrityError` в flush делать `await session.rollback()` до re-raise.

## Защита роутов

```python
# Любой авторизованный
user: CurrentUser = Depends(get_current_user)

# С конкретным пермишеном
user: CurrentUser = Depends(require_permission(P.USERS_DELETE))

# Только как dependency (без получения user объекта)
dependencies=[Depends(require_permission(P.ADMIN_PANEL))]
```

`CurrentUser` = `{id: UUID, permissions: frozenset[str]}` + метод `has_permission(str) -> bool`

Policy check (own vs all):
```python
if order.user_id != user.id and not user.has_permission(P.ORDERS_READ_ALL):
    raise HTTPException(403)
```

## Тесты

```
tests/conftest.py
  ├── DB_NAME=mydb_test  ← ставится до любого импорта в модуле
  ├── from app.factory import create_app  ← регистрирует все модели в Base.metadata
  ├── engine (session) → DROP SCHEMA CASCADE + CREATE SCHEMA + create_all + _seed()
  ├── app (session) → create_app() с override лимитеров
  └── client (function) → AsyncClient + patch FastAPILimiter
```

- `db_session` — транзакция откатывается после теста (не коммитит в БД)
- unit-тесты: `FakeUserRepo`, `FakeSessionRepo`, `FakePermissionRepo`, `FakePermissionCache`

## Makefile

```bash
make dev              # uvicorn --reload локально
make test             # pytest
make migrate          # alembic upgrade head (локально)
make migration name=X # alembic revision --autogenerate -m "X"
make seed             # python -m app.cli.seed (локально)
make init-db          # migrate + seed (локально)
make create-admin     # seed --admin (интерактивно или ADMIN_EMAIL= ADMIN_PASSWORD=)

make docker-seed      # seed в Docker контейнере
make docker-init-db   # migrate + seed в Docker
make docker-create-admin
```

## ENV файлы

| Файл | Для чего |
|------|----------|
| `service/auth_service/.env` | Локальная разработка (DB_HOST=localhost) |
| `.env` (корень) | Docker compose переменные (DB_HOST=postgres, REDIS_URL=redis://redis:6379) |

В Docker `environment:` в `docker-compose.yml` переопределяет `env_file` — поэтому хосты сервисов не нужно менять в `.env`.

## Частые ошибки

### `PendingRollbackError`
После `IntegrityError` в `flush()` — сессия в состоянии "pending rollback".  
Фикс: `await session.rollback()` перед re-raise в репозитории.

### `Can't locate revision identified by 'xxx'`
В `alembic_version` записана ревизия которой нет в `alembic/versions/`.  
Фикс: `DELETE FROM alembic_version;` → `alembic upgrade head`.

### Миграции пустые (только `pass`)
`alembic/env.py` не импортирует модели → `Base.metadata` пустой.  
Фикс: все модели явно импортированы в `env.py`.

### Пустые пермишены после логина
Roles не заполнены в БД.  
Фикс: `make seed` или `make docker-seed`.

### `relation "X" does not exist` в Docker
Старый образ — не содержит новые миграции.  
Фикс: `make build` → `make docker-init-db`.

## Docker

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && python -m app.cli.seed && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

При каждом старте контейнера: миграции (идемпотентно) → seed (идемпотентно) → сервер.
