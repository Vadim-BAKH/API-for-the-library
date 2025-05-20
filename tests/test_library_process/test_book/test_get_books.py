"""Тесты для получения списка библиотекарей через API."""

import pytest
from fastapi import status
from lib_api.business_models.library_models.models_lib import Book


@pytest.mark.asyncio
@pytest.mark.book
async def test_list_readers_success(client, db_session):
    """
    Проверяет успешное получение списка библиотекарей.

    Создаёт несколько книг, отправляет GET-запрос.
    Проверяет корректность структуры ответа.
    Проверяет LIFO сортировку по ID.
    """
    books_data = [
        {
            "title": "Тест", "author": "Ваня",
            "publication_year": 2021, "isbn": "test",
            "copies_count": 5
        },
        {
            "title": "Тест1", "author": "Ваня1",
            "publication_year": 2021, "isbn": "test1",
            "copies_count": 5
        },
        {
            "title": "Тест2", "author": "Ваня2",
            "publication_year": 2021, "isbn": "test2",
            "copies_count": 5
        },
    ]

    for data in books_data:
        book = Book(**data)
        db_session.add(book)
    await db_session.commit()

    response = await client.get("/api/librarian")
    assert response.status_code == status.HTTP_200_OK

    page = response.json()
    assert "items" in page
    assert "total" in page
    assert "page" in page
    assert "size" in page

    ids = [item["id"] for item in page["items"]]
    assert ids == list(reversed(sorted(ids)))

    titles = [item["title"] for item in page["items"]]
    for data in books_data:
        assert data["title"] in titles
