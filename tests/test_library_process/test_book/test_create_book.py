"""Тесты для создания книги через API."""

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import Book
from sqlalchemy import and_, select


@pytest.mark.asyncio
@pytest.mark.book
async def test_create_new_book_success(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет успешное создание новой книги.

    Отправляет POST-запрос с валидными данными.
    Проверяет ответ и наличие книги в базе данных.
    """
    librarian, token = create_and_authenticate_librarian
    payload = {
        "title": "Test Title",
        "author": "Test A",
        "publication_year": 2025,
        "isbn": "test",
        "copies_count": 5
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = await client.post(
        "/api/book/create", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["author"] == payload["author"]
    assert data["publication_year"] == payload["publication_year"]
    assert data.get("isbn") == payload["isbn"]
    assert data["copies_count"] == payload["copies_count"]

    book_in_db = await db_session.execute(
        select(Book).where(and_(
            Book.title == payload["title"],
            Book.author == payload["author"])
        )
    )
    book = book_in_db.scalars().first()
    assert book is not None
    assert book.title == payload["title"]


@pytest.mark.asyncio
@pytest.mark.book
async def test_create_new_book_duplicate_isbn(
        client, db_session, create_and_authenticate_librarian
):
    """
    Проверяет ошибку при создании книги с дублирующимся ISBN.

    Ожидается статус 409 Conflict с сообщением.
    """
    librarian, token = create_and_authenticate_librarian
    existing_book = Book(
        title="Тест", author="Ваня",
        publication_year=2021,
        isbn="test",
        copies_count=5
    )
    db_session.add(existing_book)
    await db_session.commit()

    payload = {
        "title": "Test Title",
        "author": "Test A",
        "publication_year": 2025,
        "isbn": "test",
        "copies_count": 5
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = await client.post(
        "/api/book/create", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_409_CONFLICT

    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_message"] == "Isbn already registered"
    assert data["detail"]["error_type"] == "HTTPException"


@pytest.mark.asyncio
@pytest.mark.book
async def test_create_new_book_missing_fields(
        client, create_and_authenticate_librarian
):
    """
    Проверяет ошибку при создании книги с неполными данными.

    Ожидается статус 422 Unprocessable Entity.
    """
    librarian, token = create_and_authenticate_librarian
    payload = {
        "title": "Test Title",

        "publication_year": 2025,
        "isbn": "test",
        "copies_count": 5
    }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = await client.post(
        "/api/book/create", json=payload, headers=headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
