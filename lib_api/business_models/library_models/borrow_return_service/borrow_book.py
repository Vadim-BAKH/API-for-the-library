"""Выдача книг из библиотеки."""

from fastapi import status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.library_models.book_crud.book_by_id import \
    get_book_by_id
from lib_api.business_models.library_models.models_lib import ReaderBook
from lib_api.business_models.library_models.reader_crud.reader_by_id import \
    get_reader_by_id
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger
from lib_api.schemas.reader_book_seeialization import BorrowedBookResponse


async def borrow_book(
        book_id: int, reader_id: int, db: AsyncSession
) -> BorrowedBookResponse:
    """
    Оформляет выдачу книги читателю.

    Проверяет доступность копий книги.
    Ограничение на количество активных заимствований у читателя.
    Создает запись о выдаче и обновляет количество доступных копий.
    :return:
        BorrowedBookResponse: Данные о выданной книге.
    """
    reader = await get_reader_by_id(reader_id, db)
    book = await get_book_by_id(book_id, db)
    if book.copies_count <= 0:
        logger.warning(f"No copies of the book ID {book_id}")
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="NoCopiesBook",
            message="No available copies to borrow",
            st_code=status.HTTP_400_BAD_REQUEST,
        )

    active_borrows_stmt = select(func.count()).select_from(ReaderBook).where(
        and_(
            ReaderBook.reader_id == reader.id,
            ReaderBook.return_date.is_(None)
        )
    )
    result = await db.execute(active_borrows_stmt)
    active_count = result.scalar_one()
    if active_count >= 3:
        logger.warning(f"Reader id {reader_id} has 3 borrowed books")
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="ReaderHasMuchBooks",
            message="Reader already has 3 borrowed books",
            st_code=status.HTTP_400_BAD_REQUEST,
        )

    borrow = ReaderBook(book_id=book_id, reader_id=reader.id)
    db.add(borrow)

    book.copies_count -= 1
    db.add(book)

    await db.commit()
    await db.refresh(borrow)
    return BorrowedBookResponse.model_validate(borrow)
