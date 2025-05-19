"""Возврат книг в библиотеку."""

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.library_models.book_crud.book_by_id import \
    get_book_by_id
from lib_api.business_models.library_models.models_lib import ReaderBook
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger
from lib_api.schemas.reader_book_seeialization import BorrowedBookResponse


async def return_book(
        borrow_id: int, db: AsyncSession
) -> BorrowedBookResponse:
    """
    Возвращает книгу в библиотеку.

    Проверяет соответствующую запись.
    Проверяет по колонке даты возврата актуальность.
    Проставляет дату возврата если проверка удачная.
    Увеличивает количество копий книги в библиотеке.
    :raise: Обработчик исключений.
    :return:
        BorrowedBookResponse: Схема с информацией о возвращенной книге.
    """
    stmt = select(ReaderBook).where(ReaderBook.id == borrow_id)
    result = await db.execute(stmt)
    borrow = result.scalars().one_or_none()

    if not borrow:
        logger.warning("Borrow record not found")
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="BorrowRecordNotFound",
            message="Borrow record not found",
            st_code=status.HTTP_404_NOT_FOUND,
        )

    if borrow.return_date is not None:
        logger.warning("Book already returned")
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="BookAlreadyReturned",
            message="Book already returned",
            st_code=status.HTTP_400_BAD_REQUEST,
        )

    # Обновляем дату возврата
    borrow.return_date = func.now()
    db.add(borrow)

    book = await get_book_by_id(borrow.book_id, db)
    book.copies_count += 1
    db.add(book)

    await db.commit()
    await db.refresh(borrow)
    return BorrowedBookResponse.model_validate(borrow)
