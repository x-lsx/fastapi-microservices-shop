# users-service/migrations/env.py
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.core.database import Base 
from app.models import category, size, product, product_size, product_image
from app.core.config import settings  

target_metadata = Base.metadata


def get_url():
    return settings.database_url  


async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    """Эта функция вызывается внутри run_sync и должна принимать ровно один аргумент"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()  # ← вот так правильно, без аргументов!


if context.is_offline_mode():
    # Оффлайн режим (генерация SQL)
    from sqlalchemy import engine_from_config, pool

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
else:
    # Онлайн режим — асинхронный
    import asyncio
    asyncio.run(run_migrations_online())