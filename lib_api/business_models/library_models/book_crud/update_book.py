"""Обновление данных книги."""

from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.decorators.error_decorator import \
    handle_db_exceptions
from lib_api.business_models.library_models.book_crud.book_by_id import \
    get_book_by_id
from lib_api.schemas.book_serialization import BookResponse, BookUpdate


@handle_db_exceptions
async def update_book_data(
    book_id: int,
    book_in: BookUpdate,
    db: AsyncSession
) -> BookResponse:
    """
    Обновляет данные книги по её идентификатору.

    Загружает существующую книгу из базы данных.
    Обновляет указанные поля.
    Сохраняет изменения и возвращает обновленные данные.
    :return:
        BookResponse: сериализованные данные книги.
    """
    book = await get_book_by_id(book_id, db)

    update_data = book_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    db.add(book)
    await db.commit()
    await db.refresh(book)
    return BookResponse.model_validate(book)
