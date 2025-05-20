"""Тесты для OAuth2-аутентификации библиотекаря."""

from os import getenv

import pytest
from dotenv import load_dotenv
from fastapi import status
from jose import jwt
from lib_api.business_models.librarian.librarian_model import Librarian
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.mark.asyncio
@pytest.mark.lib
async def test_oauth2_login_success_real_token(client, db_session):
    """
    Проверяет успешную аутентификацию библиотекаря.

    Создаёт библиотекаря, выполняет вход.
    Проверяет корректность JWT-токена и его полезной нагрузки.
    """
    load_dotenv()
    password = "secret123!"
    hashed_password = pwd_context.hash(password)
    librarian = Librarian(
        name="Test Librarian",
        email="test@example.com",
        password=hashed_password
    )
    db_session.add(librarian)
    await db_session.commit()

    form_data = {
        "username": librarian.email,
        "password": password,
    }

    response = await client.post(
        "/api/librarian/oauth2-login", data=form_data
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"

    token_parts = data["access_token"].split('.')
    assert len(token_parts) == 3

    secret_key = getenv("SECRET_KEY")
    algorithm = getenv("ALGORITHM")
    payload = jwt.decode(
        data["access_token"], secret_key, algorithms=[algorithm]
    )
    assert payload["sub"] == librarian.email


@pytest.mark.asyncio
@pytest.mark.lib
async def test_oauth2_login_wrong_password(client, db_session):
    """
    Проверяет ошибку аутентификации при неверном пароле.

    Ожидается статус 401 Unauthorized с сообщением.
    """
    password = "secret123!"
    hashed_password = pwd_context.hash(password)
    librarian = Librarian(
        name="Test Librarian",
        email="test2@example.com",
        password=hashed_password
    )
    db_session.add(librarian)
    await db_session.commit()

    form_data = {
        "username": librarian.email,
        "password": "wrongpassword",
    }

    response = await client.post(
        "/api/librarian/oauth2-login", data=form_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_type"] == "HTTPException"
    assert data["detail"]["error_message"] == "Librarian Not Found"


@pytest.mark.asyncio
@pytest.mark.lib
async def test_oauth2_login_user_not_found(client):
    """
    Проверяет ошибку аутентификации пользователя.

    Ожидается статус 401 Unauthorized с сообщением.
    """
    form_data = {
        "username": "nonexistent@example.com",
        "password": "any_password",
    }

    response = await client.post(
        "/api/librarian/oauth2-login", data=form_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_type"] == "HTTPException"
    assert data["detail"]["error_message"] == "Librarian Not Found"
