"""Тесты для удаления книги через API."""

from datetime import date

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import (Book, Reader,
                                                               ReaderBook)


@pytest.mark.asyncio
@pytest.mark.book
async def test_delete_book_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное удаление книги.

    Создаёт книгу, отправляет DELETE-запрос.
    Проверяет статус 204 No Content.
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

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(
        f"/api/book/delete/{book.id}", headers=headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
@pytest.mark.book
async def test_delete_book_with_active_borrowings(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет ошибку при удалении книги с активными заимствованиями.

    Ожидается статус 400 Bad Request с соответствующим сообщением
    """
    reader = Reader(
        name="Reader Two", email="reader2@example.com", note=""
    )
    book = Book(
        title="Book Two",
        author="Author B",
        publication_year=2019,
        isbn="isbn2",
        copies_count=0
    )
    db_session.add_all([reader, book])
    await db_session.commit()
    await db_session.refresh(reader)
    await db_session.refresh(book)

    active_borrowing = ReaderBook(
        reader_id=reader.id,
        book_id=book.id,
        borrow_date=date(2025, 5, 17),
        return_date=None
    )
    db_session.add(active_borrowing)
    await db_session.commit()

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(
        f"/api/book/delete/{book.id}", headers=headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_type"] == "HTTPException"
    assert data["detail"]["error_message"] == (
        "Book with given ID are currently issued to readers"
    )
    existing_reader = await db_session.get(Book, reader.id)

    assert existing_reader is not None


@pytest.mark.asyncio
@pytest.mark.book
async def test_delete_book_unauthorized(client):
    """
    Проверяет, что удаление книги без авторизации запрещено.

    Ожидается статус 401 Unauthorized.
    """
    book_id = 1

    response = await client.delete(f"/api/book/delete/{book_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
