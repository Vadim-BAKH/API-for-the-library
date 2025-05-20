"""Тесты для обновления данных книги через API."""

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import Book
from sqlalchemy import select


@pytest.mark.asyncio
@pytest.mark.book
async def test_update_existing_book_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное обновление данных существующей книги.

    Создаёт книгу, отправляет PUT-запрос с новыми данными.
    Проверяет обновление в ответе и базе данных.
    """
    book = Book(
        title="Тест",
        author="Ваня",
        publication_year=2021,
        isbn="test",
        copies_count=5
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    payload = {
        "publication_year": 2025,
        "isbn": "test1"
    }

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.put(
        f"/api/book/update/{book.id}", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["title"] == book.title
    assert data["author"] == book.author
    assert data["publication_year"] == payload["publication_year"]
    assert data.get("isbn") == payload["isbn"]
    assert data["copies_count"] == book.copies_count

    updated_book = await db_session.execute(
        select(Book).where(Book.id == book.id)
    )
    updated_book = updated_book.scalars().first()
    assert updated_book.title == book.title
    assert updated_book.isbn == book.isbn


@pytest.mark.asyncio
@pytest.mark.book
async def test_update_existing_book_not_found(
        client, create_and_authenticate_librarian
):
    """
    Проверяет ответ при попытке обновить несуществующую книгу.

    Ожидается статус 404 Not Found с соответствующим сообщением.
    """
    non_existent_id = 555

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    # Отправляем PUT запрос
    response = await client.put(
        f"/api/book/update/{non_existent_id}",
        json={},
        headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_type"] == "HTTPException"
    assert data["detail"]["error_message"] == "Book with given ID not found"


@pytest.mark.asyncio
@pytest.mark.book
async def test_update_existing_book_unauthorized(client):
    """
    Проверяет, что обновление данных книги без авторизации запрещено.

    Ожидается статус 401 Unauthorized.
    """
    reader_id = 1
    payload = {
        "publication_year": 2025,
        "isbn": "test1"
    }

    response = await client.put(
        f"/api/reader/update/{reader_id}", json=payload
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
