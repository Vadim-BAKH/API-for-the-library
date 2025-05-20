"""Тесты для процесса взятия книги читателем через API."""

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import (Book, Reader,
                                                               ReaderBook)
from sqlalchemy import and_, select


@pytest.mark.asyncio
@pytest.mark.br
async def test_borrow_book_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное взятие книги читателем.

    Создаёт читателя и книгу с доступными копиями.
    Отправляет запрос на взятие книги.
    Проверяет уменьшение количества копий.
    Создание записи заимствования.
    """
    reader = Reader(
        name="Reader One", email="reader1@example.com", note=""
    )
    book = Book(
        title="Book One",
        author="Author A",
        publication_year=2020,
        isbn="isbn1",
        copies_count=2
    )
    db_session.add_all([reader, book])
    await db_session.commit()
    await db_session.refresh(reader)
    await db_session.refresh(book)

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "reader_id": reader.id,
        "book_id": book.id
    }

    response = await client.post(
        "/api/librarian/borrow", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["reader_id"] == reader.id
    assert data["book_id"] == book.id

    result = await db_session.execute(
        select(Book.copies_count).where(Book.id == book.id)
    )
    copies_count = result.scalar_one()
    assert copies_count == book.copies_count - 1

    result = await db_session.execute(
        select(ReaderBook).where(
            and_(
                ReaderBook.reader_id == reader.id,
                ReaderBook.book_id == book.id,
                ReaderBook.return_date.is_(None)
            )
        )
    )
    borrow_record = result.scalars().first()
    assert borrow_record is not None


@pytest.mark.asyncio
@pytest.mark.br
async def test_borrow_book_no_copies(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет ошибку при попытке взять книгу без доступных копий.

    Ожидается статус 400 Bad Request с соответствующим сообщением.
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

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "reader_id": reader.id,
        "book_id": book.id
    }

    response = await client.post(
        "/api/librarian/borrow", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"]["error_type"] == "NoCopiesBook"
    assert data["detail"]["error_message"] == "No available copies to borrow"


@pytest.mark.asyncio
@pytest.mark.br
async def test_borrow_book_reader_limit_exceeded(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет превышение лимита заимствованных книг у читателя.

    Ожидается статус 400 Bad Request..
    """
    reader = Reader(
        name="Reader Three", email="reader3@example.com", note=""
    )
    book = Book(
        title="Book Three",
        author="Author C",
        publication_year=2018,
        isbn="isbn3",
        copies_count=5
    )
    db_session.add_all([reader, book])
    await db_session.commit()
    await db_session.refresh(reader)
    await db_session.refresh(book)

    for i_book in range(3):
        borrow = ReaderBook(reader_id=reader.id, book_id=book.id)
        db_session.add(borrow)
    await db_session.commit()

    librarian, token = create_and_authenticate_librarian
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "reader_id": reader.id,
        "book_id": book.id
    }

    response = await client.post(
        "/api/librarian/borrow", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"]["error_type"] == "ReaderHasMuchBooks"
    assert data["detail"]["error_message"] == (
        "Reader already has 3 borrowed books"
    )


@pytest.mark.asyncio
@pytest.mark.br
async def test_borrow_book_unauthorized(client):
    """
    Проверяет, что взятие книги без авторизации запрещено.

    Ожидается статус 401 Unauthorized.
    """
    payload = {
        "reader_id": 1,
        "book_id": 1
    }

    response = await client.post(
        "/api/librarian/borrow", json=payload
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
