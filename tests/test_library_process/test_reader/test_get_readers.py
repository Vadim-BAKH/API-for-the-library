"""Тесты для получения списка читателей через API."""

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import Reader


@pytest.mark.asyncio
@pytest.mark.red
async def test_list_readers_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное получение списка читателей.

    Создаёт несколько читателей, отправляет GET-запрос.
    Проверяет корректность пагинации и сортировки по имени.
    """
    readers_data = [
        {"name": "Charlie", "email": "ch@example.com", "note": "Note C"},
        {"name": "Alice", "email": "alice@example.com", "note": "Note A"},
        {"name": "Bob", "email": "bob@example.com", "note": "Note B"},
    ]
    for data in readers_data:
        reader = Reader(**data)
        db_session.add(reader)
    await db_session.commit()

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/readers", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    page = response.json()
    assert "items" in page
    assert "total" in page
    assert "page" in page
    assert "size" in page

    names = [item["name"] for item in page["items"]]
    assert names == sorted(names)

    emails = [item["email"] for item in page["items"]]
    for data in readers_data:
        assert data["email"] in emails


@pytest.mark.asyncio
@pytest.mark.red
async def test_list_readers_unauthorized(client):
    """
    Проверяет, запрет доступа к списку читателей без авторизации.

    Ожидается статус 401 Unauthorized.
    """
    response = await client.get("/api/readers")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
