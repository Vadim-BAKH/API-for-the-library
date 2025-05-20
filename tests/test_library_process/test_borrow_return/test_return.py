"""Тесты для процесса возврата книги читателем через API."""

from datetime import date

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import (Book, Reader,
                                                               ReaderBook)
from sqlalchemy import select


@pytest.mark.asyncio
@pytest.mark.br
async def test_return_book_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешный возврат книги.

    Создаёт читателя, книгу и запись заимствования.
    Отправляет запрос на возврат.
    Проверяет обновление записи, увеличение количества копий книги.
    """
    reader = Reader(name="Test Reader", email="test@example.com")
    book = Book(
        title="Test Book",
        author="Author",
        publication_year=2020,
        isbn="123",
        copies_count=1
    )
    db_session.add_all([reader, book])
    await db_session.commit()
    await db_session.refresh(reader)
    await db_session.refresh(book)

    borrow = ReaderBook(
        book_id=book.id, reader_id=reader.id, return_date=None
    )
    db_session.add(borrow)
    await db_session.commit()
    await db_session.refresh(borrow)

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "borrow_id": borrow.id
    }

    response = await client.post(
        "/api/librarian/return", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == borrow.id
    assert data["book_id"] == book.id
    assert data["reader_id"] == borrow.reader_id
    assert data["return_date"] is not None

    result = await db_session.execute(
        select(Book.copies_count).where(Book.id == book.id)
    )
    copies_count = result.scalar_one()
    assert copies_count == book.copies_count + 1

    result = await db_session.execute(
        select(ReaderBook.return_date)
        .where(ReaderBook.book_id == book.id)
    )
    return_date = result.scalar_one()
    assert return_date is not None


@pytest.mark.asyncio
@pytest.mark.br
async def test_return_book_not_found(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет попытку вернуть несуществующую запись заимствования.

    Ожидается статус 404 Not Found с соответствующим сообщением.
    """
    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "borrow_id": 888
    }

    response = await client.post(
        "/api/librarian/return", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert data["detail"]["error_type"] == "BorrowRecordNotFound"
    assert data["detail"]["error_message"] == "Borrow record not found"


@pytest.mark.asyncio
@pytest.mark.br
async def test_return_book_already_returned(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет ошибку при попытке вернуть уже возвращённую книгу.

    Ожидается статус 400 Bad Request с соответствующим сообщением.
    """
    reader = Reader(name="Test Reader", email="test@example.com")
    book = Book(
        title="Test Book",
        author="Author",
        publication_year=2020,
        isbn="123",
        copies_count=1
    )
    db_session.add_all([reader, book])
    await db_session.commit()
    await db_session.refresh(reader)
    await db_session.refresh(book)

    borrow = ReaderBook(
        book_id=book.id, reader_id=reader.id, return_date=date.today()
    )
    db_session.add(borrow)
    await db_session.commit()
    await db_session.refresh(borrow)

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "borrow_id": borrow.id
    }

    response = await client.post(
        "/api/librarian/return", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = response.json()
    assert data["detail"]["error_type"] == "BookAlreadyReturned"
    assert data["detail"]["error_message"] == "Book already returned"


@pytest.mark.asyncio
@pytest.mark.br
async def test_return_book_unauthorized(client):
    """
    Проверяет, что возврат книги без авторизации запрещён.

    Ожидается статус 401 Unauthorized.
    """
    payload = {
        "borrow_id": 1
    }

    response = await client.post("/api/librarian/return", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
