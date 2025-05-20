"""Тесты получения информации о читателе по ID через API."""

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import Reader


@pytest.mark.asyncio
@pytest.mark.red
async def test_read_reader_by_id_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное получение данных читателя по ID.

    Создаёт читателя, отправляет GET-запрос.
    Проверяет корректность возвращённых данных.
    """
    reader = Reader(
        name="Test Reader", email="reader@example.com", note="Note"
    )
    db_session.add(reader)
    await db_session.commit()
    await db_session.refresh(reader)

    librarian, token = create_and_authenticate_librarian

    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/reader/{reader.id}", headers=headers
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == reader.id
    assert data["name"] == reader.name
    assert data["email"] == reader.email
    assert data.get("note") == reader.note


@pytest.mark.asyncio
@pytest.mark.red
async def test_read_reader_by_id_not_found(
        client, create_and_authenticate_librarian
):
    """
    Проверяет ответ при запросе несуществующего читателя.

    Ожидается статус 404 Not Found с соответствующим сообщением.
    """
    non_existent_id = 777

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/reader/{non_existent_id}", headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_type"] == "NotFoundReaderID"
    assert data["detail"]["error_message"] == "Reader with given ID not found"


@pytest.mark.asyncio
@pytest.mark.red
async def test_read_reader_by_id_unauthorized(client):
    """
    Проверяет, запрет доступа к данным читателя без авторизации.

    Ожидается статус 401 Unauthorized.
    """
    reader_id = 1
    response = await client.get(f"/api/reader/{reader_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
