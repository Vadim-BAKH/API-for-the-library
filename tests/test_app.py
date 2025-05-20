"""Тесты для проверки доступности эндпоинтов API."""

import pytest
from fastapi import status

test_routes = [
    ("post", "/api/librarian/oauth2-login",
     {"username": "test", "password": "test"}),
    ("post", "/api/librarian/registration",
     {"email": "test@example.com", "password": "test"}),
    ("post", "/api/reader/create",
     {"name": "Test Reader", "email": "reader@example.com", "note": ""}),
    ("get", "/api/reader/1", None),
    ("put", "/api/reader/update/1",
     {"name": "Updated Reader", "email": "updated@example.com", "note": ""}),
    ("delete", "/api/reader/1", None),
    ("get", "/api/readers", None),
    ("post", "/api/book/create",
     {"title": "Test Book", "author": "Author", "publication_year": 2020,
      "isbn": "123", "copies_count": 1}),
    ("get", "/api/librarian", None),
    ("get", "/api/book/1", None),
    ("put", "/api/book/update/1",
     {"title": "Updated Book", "author": "Author", "publication_year": 2021,
      "isbn": "1234", "copies_count": 2}),
    ("delete", "/api/book/delete/1", None),
    ("post", "/api/librarian/borrow", {"reader_id": 1, "book_id": 1}),
    ("post", "/api/librarian/return", {"borrow_id": 1}),
    ("get", "/api/reader/1/borrowed", None),
]


@pytest.mark.asyncio
@pytest.mark.app
@pytest.mark.parametrize("method, path, json_data", test_routes)
async def test_endpoint_access(client, method, path, json_data):
    """
    Проверяет доступность эндпоинта API.

    Отправляет запрос указанным HTTP-методом на заданный путь.
    Проверяет, что эндпоинт существует, возвращает корректный статус.
    """
    http_method = getattr(client, method)
    if json_data:
        response = await http_method(path, json=json_data)
    else:
        response = await http_method(path)

    assert response.status_code != status.HTTP_404_NOT_FOUND, (
        f"Endpoint {method.upper()} {path} returned 404"
    )

    if response.status_code in (status.HTTP_401_UNAUTHORIZED,
                                status.HTTP_403_FORBIDDEN):

        pass
    else:

        assert 200 <= response.status_code < 500, (
            f"Unexpected status code {response.status_code} for "
            f"{method.upper()} {path}"
        )
