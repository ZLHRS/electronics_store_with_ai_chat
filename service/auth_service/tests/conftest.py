import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

_original_db = os.getenv("DB_NAME", "mydb")
os.environ["DB_NAME"] = os.getenv("TEST_DB_NAME", f"{_original_db}_test")

from app.factory import create_app  # noqa: E402
from app.infrastructure.db.model.base_model import Base  # noqa: E402
from app.presentation.limiters import login_limiter, refresh_limiter, register_limiter  # noqa: E402


def _pg_urls() -> tuple[str, str, str]:
    """Returns (test_url, maintenance_url, test_db_name)."""
    from app.config import setup_config

    pg = setup_config().postgres
    creds = f"{pg.user}:{pg.password.get_secret_value()}@{pg.host}:{pg.port}"
    return (
        f"postgresql+asyncpg://{creds}/{pg.db}",
        f"postgresql+asyncpg://{creds}/postgres",
        pg.db,
    )


async def _db_reachable(url: str) -> bool:
    engine = create_async_engine(url)
    try:
        async with engine.connect():
            return True
    except Exception:
        return False
    finally:
        await engine.dispose()


async def _ensure_db_exists(maintenance_url: str, db_name: str) -> None:
    engine = create_async_engine(maintenance_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            )
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        await engine.dispose()


async def _seed(conn) -> None:
    await conn.execute(text("""
        INSERT INTO roles (id, name, description) VALUES
        (gen_random_uuid(), 'admin',   'Full access'),
        (gen_random_uuid(), 'manager', 'Product and order management'),
        (gen_random_uuid(), 'user',    'Basic access')
    """))
    await conn.execute(text("""
        INSERT INTO permissions (id, code, description) VALUES
        (gen_random_uuid(), 'users.read',        'Read users'),
        (gen_random_uuid(), 'users.create',      'Create users'),
        (gen_random_uuid(), 'users.update',      'Update users'),
        (gen_random_uuid(), 'users.delete',      'Delete users'),
        (gen_random_uuid(), 'roles.read',        'Read roles'),
        (gen_random_uuid(), 'roles.assign',      'Assign roles'),
        (gen_random_uuid(), 'products.read',     'Read products'),
        (gen_random_uuid(), 'products.create',   'Create products'),
        (gen_random_uuid(), 'products.update',   'Update products'),
        (gen_random_uuid(), 'products.delete',   'Delete products'),
        (gen_random_uuid(), 'orders.read.own',   'Read own orders'),
        (gen_random_uuid(), 'orders.read.all',   'Read all orders'),
        (gen_random_uuid(), 'orders.update.own', 'Update own orders'),
        (gen_random_uuid(), 'orders.update.all', 'Update all orders')
    """))
    await conn.execute(text("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r, permissions p WHERE r.name = 'admin'
    """))
    await conn.execute(text("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r
        JOIN permissions p ON p.code IN (
            'products.read','products.create','products.update',
            'orders.read.own','orders.read.all','orders.update.own','orders.update.all'
        ) WHERE r.name = 'manager'
    """))
    await conn.execute(text("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r
        JOIN permissions p ON p.code IN (
            'users.read','products.read','orders.read.own','orders.update.own'
        ) WHERE r.name = 'user'
    """))


@pytest_asyncio.fixture(scope="session")
async def engine():
    url, maintenance_url, db_name = _pg_urls()
    if not await _db_reachable(maintenance_url):
        pytest.skip("PostgreSQL unavailable")
    await _ensure_db_exists(maintenance_url, db_name)
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.create_all)
        await _seed(conn)
    yield engine
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def app(engine):
    _app = create_app()
    _app.dependency_overrides[login_limiter] = lambda: None
    _app.dependency_overrides[register_limiter] = lambda: None
    _app.dependency_overrides[refresh_limiter] = lambda: None
    yield _app
    _app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app):
    with (
        patch("fastapi_limiter.FastAPILimiter.init", new_callable=AsyncMock),
        patch("fastapi_limiter.FastAPILimiter.close", new_callable=AsyncMock),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac


@pytest_asyncio.fixture
async def db_session(engine):
    connection = await engine.connect()
    await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    yield session
    await session.close()
    await connection.rollback()
    await connection.close()
