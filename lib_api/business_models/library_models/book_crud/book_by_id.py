"""Книга по ID."""

from typing import Optional

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.library_models.models_lib import Book
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger


async def get_book_by_id(
        book_id: int, db: AsyncSession
) -> Optional[Book]:
    """
    Получает книгу из базы данных по её идентификатору.

    Если книга с ID не найдена, вызывает обработчик ошибки.
    :return:
       Optional[Book] - модель книги опционально.
    """
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()

    if not book:
        logger.warning(f"Book with such ID {book_id} not found")
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="NotFoundBookID",
            message="Book with given ID not found",
            st_code=status.HTTP_404_NOT_FOUND,
        )
    return book
