"""Тесты для создания и получения библиотекарей."""

from os import getenv

import pytest
from dotenv import load_dotenv
from fastapi import status
from lib_api.business_models.librarian.librarian_model import Librarian
from lib_api.schemas import librarian_serialization


@pytest.mark.asyncio
@pytest.mark.lib
async def test_create_librarian_success(client, db_session):
    """
    Проверяет успешное создание нового библиотекаря.

    Создаёт библиотекаря через бизнес-логику.
    Проверяет корректность сохранённых данных.
    """
    librarian_in = librarian_serialization.LibrarianCreate(
        name="Test User",
        email="test@example.com",
        password="secret123?"
    )
    librarian = await Librarian.create_librarian(
        librarian_in=librarian_in, db=db_session
    )
    assert librarian.id is not None
    assert librarian.email == "test@example.com"
    assert librarian.name == "Test User"
    assert librarian.password != "@#secret123"


@pytest.mark.asyncio
@pytest.mark.lib
async def test_create_librarian_duplicate_email(client, db_session):
    """
    Проверяет ошибку регистрации с дублирующимся email.

    Ожидается исключение с сообщением.
    """
    librarian_in = librarian_serialization.LibrarianCreate(
        name="Test User",
        email="duplicate@example.com",
        password="secret123?"
    )

    await Librarian.create_librarian(
        librarian_in=librarian_in, db=db_session
    )

    with pytest.raises(Exception) as exc_info:
        await Librarian.create_librarian(
            librarian_in=librarian_in, db=db_session
        )
    assert "Email already registered" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.lib
async def test_get_librarian_by_email(client, db_session):
    """
    Проверяет получение библиотекаря по email.

    Создаёт библиотекаря и затем ищет его по email.
    """
    librarian_in = librarian_serialization.LibrarianCreate(
        name="Find User",
        email="findme@example.com",
        password="secret123?*"
    )
    created = await Librarian.create_librarian(
        librarian_in=librarian_in, db=db_session
    )
    found = await Librarian.get_librarian_by_email(
        db=db_session, email="findme@example.com"
    )
    assert found is not None
    assert found.id == created.id


@pytest.mark.asyncio
@pytest.mark.lib
async def test_create_new_user_endpoint_real_token(client):
    """
    Проверяет регистрацию нового библиотекаря через API.

    Отправляет POST-запрос и проверяет корректность JWT-токена.
    """
    load_dotenv()
    payload = {
        "name": "API User",
        "email": "apiuser@example.com",
        "password": "secret123!*"
    }
    response = await client.post(
        "/api/librarian/registration", json=payload
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data

    token_parts = data["access_token"].split('.')
    assert len(token_parts) == 3

    from jose import jwt
    secret_key = getenv("SECRET_KEY")
    algorithm = getenv("ALGORITHM")
    payload = jwt.decode(
        data["access_token"], secret_key, algorithms=[algorithm]
    )
    assert payload["sub"] == "apiuser@example.com"
