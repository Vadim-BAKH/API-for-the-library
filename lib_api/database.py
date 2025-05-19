"""
Модуль конфигурирует асинхронное подключение к базе данных.

PostgreSQL с помощью SQLAlchemy и asyncpg, создаёт движки.
Создаёт фабрики сессий для основной и тестовой БД.
Предоставляет функцию-генератор get_session_db.
"""

from os import getenv
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
DB_PORT = getenv("DB_PORT")
POSTGRES_DB = getenv("POSTGRES_DB")

DB_URI = \
    (f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
     f"@db:{DB_PORT}/{POSTGRES_DB}")

TEST_DB_URI = "postgresql+asyncpg://test:test@localhost:5433/test_db"

async_engine = create_async_engine(DB_URI)

test_async_engine = create_async_engine(TEST_DB_URI)

async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)

test_async_session = async_sessionmaker(
    bind=test_async_engine, expire_on_commit=False
)


async def get_session_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронный генератор сессий базы данных.

    Создания и предоставления асинхронной сессии в контексте.
    :return:Асинхронный генератор, выдающий объект AsyncSession.
    """
    async with async_session() as session:
        yield session
