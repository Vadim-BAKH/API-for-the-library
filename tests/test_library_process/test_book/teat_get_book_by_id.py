"""Тесты для получения информации о книге по ID через API."""

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import Book


@pytest.mark.asyncio
@pytest.mark.book
async def test_book_by_id_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное получение книги по ID.

    Создаёт книгу, отправляет GET-запрос.
    Проверяет корректность возвращённых данных.
    """
    book = Book(
        title="Тест",
        author="Ваня",
        publication_year=2021,
        isbn="test",
        copies_count=5)
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    librarian, token = create_and_authenticate_librarian

    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/book/{book.id}", headers=headers
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["title"] == book.title
    assert data["author"] == book.author
    assert data["publication_year"] == book.publication_year
    assert data.get("isbn") == book.isbn
    assert data["copies_count"] == book.copies_count


@pytest.mark.asyncio
@pytest.mark.book
async def test_book_by_id_not_found(
        client, create_and_authenticate_librarian
):
    """
    Проверяет ответ при запросе несуществующей книги.

    Ожидается статус 404 Not Found с сообщением.
    """
    non_existent_id = 777

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/book/{non_existent_id}", headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_type"] == "NotFoundBookID"
    assert data["detail"]["error_message"] == "Book with given ID not found"


@pytest.mark.asyncio
@pytest.mark.book
async def test_book_by_id_unauthorized(client):
    """
    Проверяет доступ к информации без авторизации.

    Ожидается статус 401 Unauthorized.:
    """
    reader_id = 1

    response = await client.get(f"/api/book/{reader_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
