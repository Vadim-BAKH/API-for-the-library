"""Тесты для получения списка взятых книг читателя через API."""

from datetime import date

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import (Book, Reader,
                                                               ReaderBook)


@pytest.mark.asyncio
@pytest.mark.br
async def test_list_borrowed_books_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное получение списка активных заимствований.

    Создаёт читателя с активными и возвращёнными книгами.
    Проверяет, что в ответе только активные заимствования.
    """
    reader = Reader(
        name="Reader Active", email="active@example.com", note=""
    )
    book1 = Book(
        title="Active Book",
        author="Author A",
        publication_year=2020,
        isbn="isbnA",
        copies_count=3
    )
    book2 = Book(
        title="Returned Book",
        author="Author B",
        publication_year=2019,
        isbn="isbnB",
        copies_count=2
    )
    db_session.add_all([reader, book1, book2])
    await db_session.commit()
    await db_session.refresh(reader)
    await db_session.refresh(book1)
    await db_session.refresh(book2)

    borrow_active = ReaderBook(
        reader_id=reader.id, book_id=book1.id, return_date=None
    )
    borrow_returned = ReaderBook(
        reader_id=reader.id, book_id=book2.id, return_date=date.today()
    )
    db_session.add_all([borrow_active, borrow_returned])
    await db_session.commit()

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/reader/{reader.id}/borrowed", headers=headers
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "borrowed_books" in data

    assert any(b["id"] == borrow_active.id for b in data["borrowed_books"])
    assert all(b["return_date"] is None for b in data["borrowed_books"])


@pytest.mark.asyncio
@pytest.mark.br
async def test_list_borrowed_books_reader_not_found(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет ответ запроса заимствований несуществующего читателя.

    Ожидается статус 404 Not Found с соответствующим сообщением.
    """
    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    non_existent_reader_id = 888
    response = await client.get(
        f"/api/reader/{non_existent_reader_id}/borrowed",
        headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"]["error_type"] == "NotFoundReaderID"
    assert data["detail"]["error_message"] == "Reader with given ID not found"


@pytest.mark.asyncio
@pytest.mark.br
async def test_list_borrowed_books_unauthorized(client):
    """
    Проверяет доступ к списку заимствований без авторизации.

    Ожидается статус 401 Unauthorized.
    """
    reader_id = 1
    response = await client.get(f"/api/reader/{reader_id}/borrowed")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
