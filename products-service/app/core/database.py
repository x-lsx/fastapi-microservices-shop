from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker 
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from .config import settings

engine = create_async_engine(settings.database_url, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Асинхронная зависимость для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронная зависимость для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def close_db():
    """Закрытие соединений с БД"""
    await engine.dispose()