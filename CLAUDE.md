# CLAUDE.md — Shop

## Инструкции для Claude

- Никогда не делай коммиты самостоятельно. Никогда не предлагай сделать коммит. Вместо этого — в конце задачи предложи готовое название коммита в формате Conventional Commits: `feat: ...`, `fix: ...`, `refactor: ...`, `chore: ...` и т.д.
- Не писать комментарии в коде. Никаких `# ...` или `"""..."""` пояснений — код должен быть самодокументируемым через названия.
- Всегда отвечать на русском языке.

---

## Контекст проекта

**Shop** — интернет-магазин с умным поиском и AI-ассистентом. В планах: семантический поиск товаров и AI-чат, который помогает пользователю находить нужные товары — задаёт уточняющие вопросы, предлагает альтернативы, учитывает контекст запроса.

Монорепозиторий с микросервисами:
```
Shop/
├── service/auth_service/     # сервис аутентификации
├── service/user_service/     # профиль, адреса, избранное, история, настройки
├── service/product_service/  # каталог товаров, категории, бренды, фильтрация
├── service/cart_service/     # корзина пользователя
├── service/order_service/    # заказы
├── service/payment_service/  # оплата и транзакции
├── nginx/                    # reverse proxy
├── postgres/init/            # SQL-скрипты инициализации БД
├── docker-compose.yml
└── Makefile
```



---

## Структура проекта

```
Shop/
├── docker-compose.yml          # postgres, redis, auth_service, user_service, product_service, cart_service, order_service, payment_service, nginx
├── .env                        # Docker-уровень: DB_HOST=postgres, REDIS_URL=redis://redis:6379, AUTH_SECRET_KEY=...
├── Makefile                    # команды (см. ниже)
├── postgres/
│   └── init/
│       ├── 01_create_userdb.sql     # создаёт БД userdb при первом старте postgres
│       ├── 02_create_productdb.sql  # создаёт БД productdb при первом старте postgres
│       ├── 03_create_cartdb.sql     # создаёт БД cartdb при первом старте postgres
│       ├── 04_create_orderdb.sql    # создаёт БД orderdb при первом старте postgres
│       └── 05_create_paymentdb.sql  # создаёт БД paymentdb при первом старте postgres
└── service/
    ├── auth_service/           # порт 8000, БД: mydb
    │   ├── main.py             # точка входа uvicorn: from app.factory import create_app; app = create_app()
    │   ├── app/
    │   │   ├── factory.py      # create_app() — FastAPI + Dishka + middleware + lifespan
    │   │   ├── config.py       # setup_config() читает .env через pydantic-settings
    │   │   ├── exceptions.py   # все доменные исключения
    │   │   ├── domain/
    │   │   │   ├── entity/     # UserEntity, SessionEntity (dataclasses, без ORM)
    │   │   │   ├── repo/       # Protocol-интерфейсы репозиториев
    │   │   │   └── permissions.py  # class P: USERS_READ = "users.read" ...
    │   │   ├── application/
    │   │   │   ├── dto/        # RegisterCommand, LoginTokens, UserResult ...
    │   │   │   └── service/
    │   │   │       └── auth_service.py  # вся бизнес-логика auth
    │   │   ├── infrastructure/
    │   │   │   ├── cache/
    │   │   │   │   └── permission_cache.py  # Redis: "permissions:user:{id}" → frozenset[str]
    │   │   │   ├── db/
    │   │   │   │   ├── model/  # SQLAlchemy модели (UserModel, RoleModel, PermissionModel ...)
    │   │   │   │   └── repo/   # SQLAlchemy реализации репозиториев
    │   │   │   ├── di/         # Dishka провайдеры (DBProvider, RedisProvider, AuthProvider)
    │   │   │   ├── mapper/     # model → entity конвертеры
    │   │   │   └── security.py # JWT encode/decode, bcrypt, SecurityService
    │   │   ├── presentation/
    │   │   │   ├── api/
    │   │   │   │   └── auth_api.py  # FastAPI роуты
    │   │   │   ├── deps.py     # CurrentUser, get_current_user, require_permission()
    │   │   │   └── exception.py # exception handlers
    │   │   └── cli/
    │   │       └── seed.py     # идемпотентный seed ролей и пермишенов
    │   ├── alembic/
    │   │   ├── env.py          # ВАЖНО: импортирует все модели для autogenerate
    │   │   └── versions/       # миграции — только схема, без данных
    │   └── tests/
    │       ├── conftest.py     # engine, app, client, db_session фикстуры
    │       ├── unit/           # FakeRepo, FakeCache — без БД
    │       ├── integration/    # реальная БД через db_session
    │       ├── api/            # httpx ASGITransport
    │       └── e2e/            # полный flow через httpx
    ├── user_service/           # порт 8001, БД: userdb
    │   ├── main.py
    │   ├── app/
    │   │   ├── factory.py
    │   │   ├── config.py       # JWTConfig вместо AuthConfig — только decode, без bcrypt
    │   │   ├── exceptions.py
    │   │   ├── domain/
    │   │   │   ├── entity/     # UserProfileEntity, AddressEntity, FavoriteEntity, ViewHistoryEntity, PreferencesEntity
    │   │   │   └── repo/       # Protocol-интерфейсы (5 репозиториев)
    │   │   ├── application/
    │   │   │   ├── dto/        # команды и результаты для всех доменов
    │   │   │   └── service/    # UserProfileService, AddressService, FavoriteService, ViewHistoryService, PreferencesService
    │   │   ├── infrastructure/
    │   │   │   ├── db/
    │   │   │   │   ├── model/  # UserProfileModel, AddressModel, FavoriteModel, ViewHistoryModel, PreferencesModel
    │   │   │   │   └── repo/   # SQLAlchemy реализации
    │   │   │   ├── di/         # Dishka провайдеры (DBProvider, RedisProvider, UserProvider)
    │   │   │   ├── mapper/     # model → entity конвертеры
    │   │   │   └── jwt_service.py  # только decode access token (без bcrypt, без сессий)
    │   │   └── presentation/
    │   │       ├── api/        # user_api, address_api, favorite_api, view_history_api, preferences_api
    │   │       ├── deps.py     # CurrentUser{auth_user_id, profile_id}, get_current_user
    │   │       └── exception.py
    │   ├── alembic/
    │   │   ├── env.py
    │   │   └── versions/
    │   └── tests/
    │       ├── conftest.py
    │       ├── unit/
    │       ├── integration/
    │       ├── api/
    │       └── e2e/
    ├── product_service/        # порт 8002, БД: productdb
    │   ├── main.py
    │   ├── app/
    │   │   ├── factory.py
    │   │   ├── config.py       # JWTConfig — только decode; нет bcrypt
    │   │   ├── exceptions.py
    │   │   ├── domain/
    │   │   │   ├── entity/     # ProductEntity, CategoryEntity, BrandEntity + вложенные Image/Attribute
    │   │   │   ├── repo/       # Protocol-интерфейсы (ProductRepo, CategoryRepo, BrandRepo)
    │   │   │   └── permissions.py  # class P: PRODUCTS_CREATE/UPDATE/DELETE
    │   │   ├── application/
    │   │   │   ├── dto/        # команды и результаты; ProductFilter — объект фильтрации
    │   │   │   └── service/    # ProductService, CategoryService, BrandService
    │   │   ├── infrastructure/
    │   │   │   ├── db/
    │   │   │   │   ├── model/  # ProductModel, CategoryModel, BrandModel, ProductImageModel, ProductAttributeModel
    │   │   │   │   └── repo/   # SQLAlchemy реализации; product_repo содержит логику фильтрации
    │   │   │   ├── di/         # Dishka провайдеры (DBProvider, RedisProvider, ProductProvider)
    │   │   │   ├── mapper/     # model → entity конвертеры
    │   │   │   ├── jwt_service.py       # только decode access token
    │   │   │   ├── permission_cache.py  # read-only доступ к Redis ключам auth_service
    │   │   │   └── slugify.py           # авто-генерация slug из названия
    │   │   └── presentation/
    │   │       ├── api/        # product_api, category_api, brand_api, health_api
    │   │       ├── deps.py     # CurrentUser{id, permissions}, get_current_user, require_permission()
    │   │       └── exception.py
    │   ├── alembic/
    │   │   ├── env.py
    │   │   └── versions/
    │   └── tests/
    │       ├── conftest.py
    │       ├── unit/           # FakeProductRepo + тесты ProductService и slugify
    │       ├── integration/    # реальная БД — фильтрация по атрибутам
    │       ├── api/
    │       └── e2e/            # полный CRUD flow + категории/бренды
    ├── cart_service/           # порт 8003, БД: cartdb
    │   ├── main.py
    │   ├── app/
    │   │   ├── factory.py
    │   │   ├── config.py       # + ProductServiceConfig: PRODUCT_SERVICE_URL
    │   │   ├── exceptions.py
    │   │   ├── domain/
    │   │   │   ├── entity/     # CartEntity, CartItemEntity, CartStatus
    │   │   │   └── repo/       # CartRepository, CartItemRepository (Protocol)
    │   │   ├── application/
    │   │   │   ├── dto/        # AddItemCommand, UpdateItemCommand, CartResult, ProductSnapshot
    │   │   │   └── service/
    │   │   │       └── cart_service.py  # get_cart, add_item, update_item, remove_item, clear_cart
    │   │   ├── infrastructure/
    │   │   │   ├── db/
    │   │   │   │   ├── model/  # CartModel, CartItemModel
    │   │   │   │   └── repo/   # SQLAlchemyCartRepo, SQLAlchemyCartItemRepo
    │   │   │   ├── di/         # DBProvider, RedisProvider, CartProvider (httpx.AsyncClient APP scope)
    │   │   │   ├── mapper/     # cart_mapper.py
    │   │   │   ├── jwt_service.py
    │   │   │   ├── permission_cache.py
    │   │   │   └── product_client.py   # ProductServiceClient — httpx GET /api/v1/products/{id}
    │   │   └── presentation/
    │   │       ├── api/
    │   │       │   └── cart_api.py  # GET/POST/PATCH/DELETE /cart и /cart/items/{product_id}
    │   │       ├── deps.py     # CurrentUser{id}, get_current_user (без permissions — корзина личная)
    │   │       └── exception.py
    │   ├── alembic/
    │   │   ├── env.py
    │   │   └── versions/       # partial unique index uq_carts_user_active WHERE status='active'
    │   └── tests/
    │       ├── conftest.py
    │       ├── unit/           # FakeCartRepo, FakeCartItemRepo, FakeProductClient
    │       ├── integration/    # реальная БД — корзина, позиции, количество
    │       ├── api/
    │       └── e2e/            # полный flow: добавление, обновление, удаление, очистка
    ├── order_service/          # порт 8004, БД: orderdb
    │   ├── main.py
    │   ├── app/
    │   │   ├── factory.py
    │   │   ├── config.py       # + CartServiceConfig: CART_SERVICE_URL, ProductServiceConfig: PRODUCT_SERVICE_URL
    │   │   ├── exceptions.py
    │   │   ├── domain/
    │   │   │   ├── entity/     # OrderEntity, OrderItemEntity, OrderStatus, CreateOrder, CreateOrderItem
    │   │   │   ├── repo/       # OrderRepository (Protocol)
    │   │   │   └── permissions.py  # class P: ORDERS_READ_OWN/ALL, ORDERS_UPDATE_OWN/ALL
    │   │   ├── application/
    │   │   │   ├── dto/        # CreateOrderCommand, UpdateStatusCommand, OrderResult, OrderItemResult
    │   │   │   └── service/
    │   │   │       └── order_service.py  # create_order, get_order, list_orders, cancel_order, update_status
    │   │   ├── infrastructure/
    │   │   │   ├── db/
    │   │   │   │   ├── model/  # OrderModel, OrderItemModel
    │   │   │   │   └── repo/   # SQLAlchemyOrderRepo
    │   │   │   ├── di/         # DBProvider, RedisProvider, OrderProvider (два httpx.AsyncClient: cart + product)
    │   │   │   ├── mapper/     # order_mapper.py
    │   │   │   ├── jwt_service.py
    │   │   │   ├── permission_cache.py
    │   │   │   ├── cart_client.py     # CartServiceClient — GET/DELETE /api/v1/cart (с cookie access_token)
    │   │   │   └── product_client.py  # ProductServiceClient — GET /api/v1/products/{id}
    │   │   └── presentation/
    │   │       ├── api/
    │   │       │   └── order_api.py  # POST/GET /orders, GET/PATCH /orders/{id}, PATCH /orders/{id}/cancel, PATCH /orders/{id}/status
    │   │       ├── deps.py     # CurrentUser{id, permissions}, get_current_user, require_permission()
    │   │       └── exception.py
    │   ├── alembic/
    │   │   ├── env.py
    │   │   └── versions/
    │   └── tests/
    │       ├── conftest.py
    │       ├── unit/           # FakeOrderRepo, FakeCartClient, FakeProductClient
    │       ├── integration/    # реальная БД — заказы, позиции, статусы
    │       ├── api/
    │       └── e2e/            # полный flow: создание заказа из корзины, отмена
    └── payment_service/        # порт 8005, БД: paymentdb
        ├── main.py
        ├── app/
        │   ├── factory.py
        │   ├── config.py       # + OrderServiceConfig: ORDER_SERVICE_URL
        │   ├── exceptions.py
        │   ├── domain/
        │   │   ├── entity/     # PaymentEntity, PaymentEventEntity, PaymentStatus, PaymentProvider
        │   │   └── repo/       # PaymentRepository, PaymentEventRepository (Protocol)
        │   ├── application/
        │   │   ├── dto/        # CreatePaymentCommand, WebhookPayload, PaymentResult
        │   │   └── service/
        │   │       └── payment_service.py  # create_payment, get_payment, refund_payment, handle_webhook
        │   ├── infrastructure/
        │   │   ├── db/
        │   │   │   ├── model/  # PaymentModel, PaymentEventModel
        │   │   │   └── repo/   # SQLAlchemyPaymentRepo, SQLAlchemyPaymentEventRepo
        │   │   ├── di/         # DBProvider, RedisProvider, PaymentProvider (httpx.AsyncClient APP scope)
        │   │   ├── mapper/     # payment_mapper.py
        │   │   ├── jwt_service.py
        │   │   ├── permission_cache.py
        │   │   └── order_client.py   # OrderServiceClient — GET /api/v1/orders/{id}, POST уведомления
        │   └── presentation/
        │       ├── api/
        │       │   ├── payment_api.py   # POST/GET /payments, POST /payments/{id}/refund
        │       │   └── webhook_api.py   # POST /webhooks/{kaspi,stripe,freedompay} — публичные, без JWT
        │       ├── deps.py     # CurrentUser{id}, get_current_user (без permissions — платежи личные)
        │       └── exception.py
        ├── alembic/
        │   ├── env.py
        │   └── versions/
        └── tests/
            ├── conftest.py
            ├── unit/           # FakePaymentRepo, FakePaymentEventRepo, FakeOrderClient
            ├── integration/    # реальная БД — платёж, события, статусы
            ├── api/
            └── e2e/            # полный flow: создание → webhook → paid → уведомление order_service
```

## Ключевые архитектурные решения

### Разделение ответственности между сервисами
- **Auth Service** = кто ты и можно ли тебе войти: логин, пароль, JWT, сессии, роли/пермишены
- **User Service** = твой профиль: имя, адреса, избранное, история просмотров, настройки
- **Product Service** = каталог: товары, категории, бренды, характеристики, фильтрация
- **Cart Service** = корзина: позиции, количество, цена на момент добавления, итог
- **Order Service** = заказы: оформление из корзины (snapshot имён товаров), статусы, история
- **Payment Service** = оплата: создание платежей, webhook от провайдеров, возвраты

Связь между сервисами: `user_profiles.auth_user_id` = `users.id` из auth_service. Профиль создаётся лениво при первом обращении к user_service.

**Права в product_service и cart_service**: сервисы читают `permissions:user:{id}` из того же Redis, куда auth_service пишет после логина — без межсервисных HTTP-вызовов.

**Межсервисный вызов в cart_service**: при добавлении товара cart_service делает `GET product_service/api/v1/products/{id}` через `ProductServiceClient` (httpx). Получает `price` и `status`. Если product_service недоступен при отдаче корзины — `product` snapshot в ответе будет `null`, но позиции остаются.

**Межсервисные вызовы в order_service**: при создании заказа — `GET cart_service/api/v1/cart` (с cookie access_token) и `GET product_service/api/v1/products/{id}` для каждой позиции (проверка статуса, snapshot имени). После создания заказа — `DELETE cart_service/api/v1/cart` для очистки корзины. Два отдельных `httpx.AsyncClient` на APP scope.

**Межсервисные вызовы в payment_service**: при создании платежа — `GET order_service/api/v1/orders/{id}` для проверки заказа (владелец, статус `pending_payment`, сумма). После webhook от провайдера — `POST order_service/api/v1/orders/{id}/payment-confirmed` или `/payment-failed`. Если order_service недоступен при уведомлении — ошибка логируется, но не пробрасывается (платёж уже сохранён).

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

### auth_service

| Scope | Провайдер | Что создаёт |
|-------|-----------|-------------|
| APP   | ConfigProvider | Config |
| APP   | DBProvider | AsyncEngine, async_sessionmaker |
| APP   | RedisProvider | redis.Redis, PermissionCache |
| APP   | AuthProvider | AuthConfig, SecurityService |
| REQUEST | DBProvider | AsyncSession |
| REQUEST | AuthProvider | UserRepo, SessionRepo, PermissionRepo, AuthService |

### user_service

| Scope | Провайдер | Что создаёт |
|-------|-----------|-------------|
| APP   | ConfigProvider | Config |
| APP   | DBProvider | AsyncEngine, async_sessionmaker |
| APP   | RedisProvider | redis.Redis |
| APP   | UserProvider | JWTConfig, JWTService |
| REQUEST | DBProvider | AsyncSession |
| REQUEST | UserProvider | UserProfileRepo, AddressRepo, FavoriteRepo, ViewHistoryRepo, PreferencesRepo, все сервисы |

### product_service

| Scope | Провайдер | Что создаёт |
|-------|-----------|-------------|
| APP   | ConfigProvider | Config |
| APP   | DBProvider | AsyncEngine, async_sessionmaker |
| APP   | RedisProvider | redis.Redis, PermissionCache |
| APP   | ProductProvider | JWTConfig, JWTService |
| REQUEST | DBProvider | AsyncSession |
| REQUEST | ProductProvider | ProductRepo, CategoryRepo, BrandRepo, ProductService, CategoryService, BrandService |

### cart_service

| Scope | Провайдер | Что создаёт |
|-------|-----------|-------------|
| APP   | ConfigProvider | Config |
| APP   | DBProvider | AsyncEngine, async_sessionmaker |
| APP   | RedisProvider | redis.Redis, PermissionCache |
| APP   | CartProvider | JWTConfig, JWTService, httpx.AsyncClient, ProductServiceClient |
| REQUEST | DBProvider | AsyncSession |
| REQUEST | CartProvider | CartRepo, CartItemRepo, CartService |

### order_service

| Scope | Провайдер | Что создаёт |
|-------|-----------|-------------|
| APP   | ConfigProvider | Config |
| APP   | DBProvider | AsyncEngine, async_sessionmaker |
| APP   | RedisProvider | redis.Redis, PermissionCache |
| APP   | OrderProvider | JWTConfig, JWTService, httpx.AsyncClient (cart), httpx.AsyncClient (product), CartServiceClient, ProductServiceClient |
| REQUEST | DBProvider | AsyncSession |
| REQUEST | OrderProvider | OrderRepo, OrderService |

### payment_service

| Scope | Провайдер | Что создаёт |
|-------|-----------|-------------|
| APP   | ConfigProvider | Config |
| APP   | DBProvider | AsyncEngine, async_sessionmaker |
| APP   | RedisProvider | redis.Redis, PermissionCache |
| APP   | PaymentProvider | JWTConfig, JWTService, httpx.AsyncClient, OrderServiceClient |
| REQUEST | DBProvider | AsyncSession |
| REQUEST | PaymentProvider | PaymentRepo, PaymentEventRepo, PaymentService |

`httpx.AsyncClient` создаётся один раз на APP scope и закрывается через async generator provider при shutdown контейнера.

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
# auth_service
make dev              # uvicorn --reload локально (порт 8000)
make test             # pytest
make migrate          # alembic upgrade head (локально)
make migration name=X # alembic revision --autogenerate -m "X"
make seed             # python -m app.cli.seed (локально)
make init-db          # migrate + seed (локально)
make create-admin     # seed --admin (интерактивно или ADMIN_EMAIL= ADMIN_PASSWORD=)

make docker-seed      # seed в Docker контейнере
make docker-init-db   # migrate + seed в Docker
make docker-create-admin

# user_service
make user-dev              # uvicorn --reload локально (порт 8001)
make user-test             # pytest
make user-migrate          # alembic upgrade head (локально)
make user-migration name=X # alembic revision --autogenerate -m "X"
make user-lint
make user-format

# product_service
make product-dev              # uvicorn --reload локально (порт 8002)
make product-test             # pytest
make product-migrate          # alembic upgrade head (локально)
make product-migration name=X # alembic revision --autogenerate -m "X"
make product-lint
make product-format

# cart_service
make cart-dev              # uvicorn --reload локально (порт 8003)
make cart-test             # pytest
make cart-migrate          # alembic upgrade head (локально)
make cart-migration name=X # alembic revision --autogenerate -m "X"
make cart-lint
make cart-format

# order_service
make order-dev              # uvicorn --reload локально (порт 8004)
make order-test             # pytest
make order-migrate          # alembic upgrade head (локально)
make order-migration name=X # alembic revision --autogenerate -m "X"
make order-lint
make order-format

# payment_service
make payment-dev              # uvicorn --reload локально (порт 8005)
make payment-test             # pytest
make payment-migrate          # alembic upgrade head (локально)
make payment-migration name=X # alembic revision --autogenerate -m "X"
make payment-lint
make payment-format

# Docker — отдельные сервисы
make up-user / build-user / down-user
make up-product / build-product / down-product
make up-cart / build-cart / down-cart
make up-order / build-order / down-order
make up-payment / build-payment / down-payment
```

## ENV файлы

| Файл | Для чего |
|------|----------|
| `service/auth_service/.env` | Локальная разработка auth_service (DB_HOST=localhost) |
| `service/user_service/.env` | Локальная разработка user_service (DB_HOST=localhost, DB_NAME=userdb) |
| `service/product_service/.env` | Локальная разработка product_service (DB_HOST=localhost, DB_NAME=productdb) |
| `service/cart_service/.env` | Локальная разработка cart_service (DB_HOST=localhost, DB_NAME=cartdb, PRODUCT_SERVICE_URL=http://localhost:8002) |
| `service/order_service/.env` | Локальная разработка order_service (DB_HOST=localhost, DB_NAME=orderdb, CART_SERVICE_URL=http://localhost:8003, PRODUCT_SERVICE_URL=http://localhost:8002) |
| `service/payment_service/.env` | Локальная разработка payment_service (DB_HOST=localhost, DB_NAME=paymentdb, ORDER_SERVICE_URL=http://localhost:8004) |
| `.env` (корень) | Docker compose переменные (DB_HOST=postgres, REDIS_URL=redis://redis:6379, AUTH_SECRET_KEY=...) |

В Docker `environment:` в `docker-compose.yml` переопределяет `env_file` — поэтому хосты сервисов не нужно менять в `.env`.

**Общий секрет**: `AUTH_SECRET_KEY` должен быть одинаковым во всех сервисах. В Docker он берётся из корневого `.env` через `${AUTH_SECRET_KEY}` и переопределяет значение из `env_file` сервиса.

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
# auth_service
CMD ["sh", "-c", "alembic upgrade head && python -m app.cli.seed && uvicorn main:app --host 0.0.0.0 --port 8000"]

# user_service
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8001"]

# product_service
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8002"]

# cart_service
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8003"]

# order_service
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8004"]

# payment_service
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8005"]
```

При каждом старте контейнера: миграции (идемпотентно) → сервер.

### Nginx маршрутизация

```
/api/v1/users/*      →  user_service:8001
/api/v1/products/*   →  product_service:8002
/api/v1/categories/* →  product_service:8002
/api/v1/brands/*     →  product_service:8002
/api/v1/cart/*       →  cart_service:8003
/api/v1/orders/*     →  order_service:8004
/api/v1/payments/*   →  payment_service:8005
/api/v1/webhooks/*   →  payment_service:8005
/*                   →  auth_service:8000
```

### Базы данных

Init-скрипты запускаются postgres при **первом** старте (только если `postgres_data` volume пустой).  
При существующем volume — создать вручную:
```bash
docker compose exec postgres psql -U postgres -c "CREATE DATABASE userdb;"
docker compose exec postgres psql -U postgres -c "CREATE DATABASE productdb;"
docker compose exec postgres psql -U postgres -c "CREATE DATABASE cartdb;"
docker compose exec postgres psql -U postgres -c "CREATE DATABASE orderdb;"
docker compose exec postgres psql -U postgres -c "CREATE DATABASE paymentdb;"
```
