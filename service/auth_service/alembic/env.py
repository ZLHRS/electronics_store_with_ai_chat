import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.config import setup_config
from app.infrastructure.db.model.base_model import Base
import app.infrastructure.db.model.user_model  # noqa: F401
import app.infrastructure.db.model.user_session_model  # noqa: F401
import app.infrastructure.db.model.role_model  # noqa: F401
import app.infrastructure.db.model.permission_model  # noqa: F401
import app.infrastructure.db.model.user_role_model  # noqa: F401
import app.infrastructure.db.model.role_permission_model  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db = setup_config().postgres.get_url()
config.set_main_option("sqlalchemy.url", db)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=db,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
