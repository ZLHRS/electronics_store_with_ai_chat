import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

_original_db = os.getenv("DB_NAME", "cartdb")
os.environ["DB_NAME"] = os.getenv("TEST_DB_NAME", f"{_original_db}_test")

from app.factory import create_app  # noqa: E402
from app.infrastructure.db.model.base_model import Base  # noqa: E402
from app.presentation.limiters import cart_limiter  # noqa: E402


def _pg_urls() -> tuple[str, str, str]:
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
        await conn.execute(
            text("CREATE UNIQUE INDEX uq_carts_user_active ON carts(user_id) WHERE status = 'active'")
        )
    yield engine
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def app(engine):
    _app = create_app()
    _app.dependency_overrides[cart_limiter] = lambda: None
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
