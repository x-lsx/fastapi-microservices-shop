import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from alembic import context

from app.core.database import Base  # твой базовый класс моделей
# Импорт моделей — важно, чтобы SQLAlchemy зарегистрировал все таблицы в metadata
# Подключаем классы моделей через пакет, чтобы при автогенерации Alembic видел схемы
from app.models import order
# Alembic Config
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

# URL к базе (asyncpg для PostgreSQL)
import os

# берем URL из alembic.ini (если указан) или из переменной окружения DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
if not DATABASE_URL:
    # fallback — sqlite dev DB
    DATABASE_URL = "sqlite+aiosqlite:///./shop.db"

def run_migrations_offline():
    """Миграции без подключения к базе"""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Миграции с асинхронным движком"""
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection: Connection):
    """Функция для синхронного запуска миграций через run_sync"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


main()
