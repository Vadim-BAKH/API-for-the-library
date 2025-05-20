"""Тесты для создания читателя через API."""

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import Reader
from sqlalchemy import select


@pytest.mark.asyncio
@pytest.mark.red
async def test_create_new_reader_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное создание нового читателя.

    Отправляет POST-запрос с валидными данными.
    Проверяет ответ и наличие записи в базе данных.
    """
    librarian, token = create_and_authenticate_librarian
    payload = {
        "name": "Test Reader",
        "email": "reader@example.com",
        "note": "Test note"
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = await client.post(
        "/api/reader/create", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data.get("note") == payload["note"]

    reader_in_db = await db_session.execute(
        select(Reader).where(Reader.email == payload["email"])
    )
    reader = reader_in_db.scalars().first()
    assert reader is not None
    assert reader.name == payload["name"]


@pytest.mark.asyncio
@pytest.mark.red
async def test_create_new_reader_duplicate_email(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет ошибку при попытке создать читателя.

    Email уже зарегистрирован.
    Ожидается статус 409 Conflict и соответствующее сообщение.
    """
    librarian, token = create_and_authenticate_librarian
    existing_reader = Reader(
        name="Existing Reader", email="duplicate@example.com", note=""
    )
    db_session.add(existing_reader)
    await db_session.commit()

    payload = {
        "name": "New Reader",
        "email": "duplicate@example.com",  # тот же email
        "note": "Another note"
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = await client.post(
        "/api/reader/create", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_409_CONFLICT

    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_message"] == "Email already registered"
    assert data["detail"]["error_type"] == "HTTPException"


@pytest.mark.asyncio
@pytest.mark.red
async def test_create_new_reader_missing_fields(
        client, create_and_authenticate_librarian
):
    """
    Проверяет ошибку при создании читателя.

    Неполные данные.
    Ожидается статус 422 Unprocessable Entity.
    """
    librarian, token = create_and_authenticate_librarian
    payload = {
        "email": "incomplete@example.com"
    }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = await client.post(
        "/api/reader/create", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
