"""Тесты для удаления читателей через API."""

from datetime import date

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import (Book, Reader,
                                                               ReaderBook)


@pytest.mark.asyncio
@pytest.mark.red
async def test_delete_reader_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное удаление читателя.

    Отправляет DELETE-запрос и проверяет статус 204 No Content.
    """
    reader = Reader(
        name="Reader To Delete", email="delete@example.com", note=""
    )
    db_session.add(reader)
    await db_session.commit()
    await db_session.refresh(reader)

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(
        f"/api/reader/{reader.id}", headers=headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
@pytest.mark.red
async def test_delete_reader_with_active_borrowings(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет ошибку при удалении читателя с книгами.

    Ожидается статус 400 Bad Request с сообщением.
    """
    reader = Reader(
        name="Reader Two", email="reader2@example.com", note=""
    )
    book = Book(
        title="Book Two", author="Author B",
        publication_year=2019, isbn="isbn2", copies_count=0
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
        f"/api/reader/{reader.id}", headers=headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_type"] == "HTTPException"
    assert (data["detail"]["error_message"] == "Reader has active borrowings")

    existing_reader = await db_session.get(Reader, reader.id)
    assert existing_reader is not None


@pytest.mark.asyncio
@pytest.mark.red
async def test_delete_reader_unauthorized(client):
    """
    Проверяет, что удаление читателя без авторизации запрещено.

    Ожидается статус 401 Unauthorized.
    """
    reader_id = 1

    response = await client.delete(f"/api/reader/{reader_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
