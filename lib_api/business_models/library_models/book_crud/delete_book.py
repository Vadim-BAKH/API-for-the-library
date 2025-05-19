"""Удаление книги."""

from fastapi import status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.decorators.error_decorator import \
    handle_db_exceptions
from lib_api.business_models.library_models.book_crud.book_by_id import \
    get_book_by_id
from lib_api.business_models.library_models.models_lib import ReaderBook
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger


@handle_db_exceptions
async def delete_book(
        book_id: int, db: AsyncSession
) -> None:
    """
    Удаляет книгу без активных задач из базы данных.

    Проверяет наличие активных выдач.
    На активные выдачи вызывает обработчик ошибки с кодом 400.

    :return: None
    """
    book = await get_book_by_id(book_id, db)
    count_stmt = select(func.count()).select_from(ReaderBook).where(
        and_(
            ReaderBook.book_id == book_id,
            ReaderBook.return_date.is_(None)
        )
    )
    result = await db.execute(count_stmt)
    active_count = result.scalar_one()

    if active_count > 0:
        logger.warning(
            f"Bad delete Book ID {book_id}"
            f" are currently issued to readers"
        )
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="BadDeleteBook",
            message="Book with given ID are currently issued to readers",
            st_code=status.HTTP_400_BAD_REQUEST,
        )

    await db.delete(book)
    await db.commit()
