"""Конфигуратор тестов."""

from typing import AsyncGenerator

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from lib_api.app import app
from lib_api.business_models.base_model.base_model import Base
from lib_api.business_models.librarian.librarian_model import Librarian
from lib_api.database import (get_session_db, test_async_engine,
                              test_async_session)
from lib_api.schemas import librarian_serialization
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
async def override_dependencies():
    """Переопределяет основную сессию на тестовую."""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """Создает сессию для тестов."""
        async with test_async_session() as session:
            yield session

    app.dependency_overrides[get_session_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает тестовую сессию базы данных."""
    async with test_async_session() as session:
        yield session


@pytest.fixture(autouse=True)
async def test_database() -> AsyncGenerator:
    """Фикстура для управления миграциями."""
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
    """Возвращает асинхронный клиент."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture
async def create_and_authenticate_librarian(db_session, client):
    """Фикстура для регистрации и авторизации библиотекаря."""
    librarian_in = librarian_serialization.LibrarianCreate(
        name="Test User",
        email="test@example.com",
        password="secret123?"
    )
    librarian = await Librarian.create_librarian(
        librarian_in=librarian_in, db=db_session
    )

    form_data = {
        "username": librarian.email,
        "password": "secret123?"
    }
    response = await client.post("/api/librarian/oauth2-login", data=form_data)
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]

    return librarian, token
