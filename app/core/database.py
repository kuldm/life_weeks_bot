from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# from src.logger import logger

metadata = MetaData()


class Base(DeclarativeBase):
    """Базовый класс для моделей SQLAlchemy"""

    metadata = metadata


engine_async = create_async_engine(
    settings.async_database_url,
    # echo=settings.database_echo,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = sessionmaker(
    bind=engine_async,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Инициализация подключения к базе данных"""
    try:
        # Проверяем соединение с базой данных
        async with engine_async.begin() as conn:
            await conn.run_sync(lambda _: None)
        # logger.info("Database connection established successfully")
    except Exception as e:
        # logger.error(f"Error connecting to database: {e}")
        raise


async def close_db() -> None:
    """Закрытие соединения с базой данных"""
    try:
        await engine_async.dispose()
        # logger.info("Database connection closed successfully")
    except Exception as e:
        # logger.error(f"Error closing database connection: {e}")
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии базы данных"""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
