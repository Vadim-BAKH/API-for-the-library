"""Проверка уникального isbn."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.library_models.models_lib import Book


async def get_book_by_isbn(
        isbn: str, db: AsyncSession
) -> Optional[Book]:
    """
    Получает книгу из базы данных по isbn.

    :return:
        Optional[Book]: Объект книги, если найден, иначе None.
    """
    result = await db.execute(
        select(Book).where(Book.isbn == isbn)
    )
    return result.scalars().first()
