"""Тесты для обновления данных читателя через API."""

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import Reader
from sqlalchemy import select


@pytest.mark.asyncio
@pytest.mark.red
async def test_update_existing_reader_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное обновление данных существующего читателя.

    Отправляет PUT-запрос с новыми данными.
    Проверяет обновление в ответе и базе данных.
    """
    reader = Reader(
        name="Old Name", email="old@example.com", note="Old Note"
    )
    db_session.add(reader)
    await db_session.commit()
    await db_session.refresh(reader)

    # Данные для обновления
    payload = {
        "name": "New Name",
        "note": "New Note"
    }

    # Получаем токен библиотекаря
    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    # Отправляем PUT запрос
    response = await client.put(
        f"/api/reader/update/{reader.id}",
        json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == reader.id
    assert data["name"] == payload["name"]
    assert data["email"] == reader.email
    assert data["note"] == payload["note"]
    await db_session.refresh(reader)

    updated_reader = await db_session.execute(
        select(Reader).where(Reader.id == reader.id)
    )
    updated_reader = updated_reader.scalars().first()
    assert updated_reader.name == payload["name"]
    assert updated_reader.note == payload["note"]


@pytest.mark.asyncio
@pytest.mark.red
async def test_update_existing_reader_not_found(
        client, create_and_authenticate_librarian
):
    """
    Проверяет ответ при попытке обновить несуществующего читателя.

    Ожидается статус 404 Not Found с соответствующим сообщением.
    """
    non_existent_id = 27

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    # Отправляем PUT запрос
    response = await client.put(
        f"/api/reader/update/{non_existent_id}",
        json={}, headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_type"] == "HTTPException"
    assert data["detail"]["error_message"] == "Reader with given ID not found"


@pytest.mark.asyncio
@pytest.mark.red
async def test_update_existing_reader_unauthorized(client):
    """
    Проверяет запрет обновление данных читателя без авторизации.

    Ожидается статус 401 Unauthorized.
    """
    reader_id = 1
    payload = {"name": "New Name"}

    response = await client.put(
        f"/api/reader/update/{reader_id}", json=payload
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
