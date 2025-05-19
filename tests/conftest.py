"""Конфигуратор тестов"""

from typing import AsyncGenerator

import pytest
from lib_api.app import app
from lib_api.business_models.base_model.base_model import  Base
from lib_api.database import (get_session_db, test_async_engine,
                              test_async_session)


from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
async def override_dependencies():
    """Переопределяет основную сессию на тестовую"""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """Создает сессию для тестов"""
        async with test_async_session() as session:
            yield session

    app.dependency_overrides[get_session_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def test_database() -> AsyncGenerator:
    """Фикстура для управления миграциями"""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield

    finally:
        async with test_async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_async_engine.dispose()


@pytest.fixture
async def client():
    """Возвращает асинхронный клиент"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

