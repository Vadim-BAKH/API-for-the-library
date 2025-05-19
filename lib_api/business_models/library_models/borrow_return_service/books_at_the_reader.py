"""Актуальный список книг у читателя."""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.library_models.models_lib import ReaderBook
from lib_api.business_models.library_models.reader_crud.reader_by_id import \
    get_reader_by_id
from lib_api.schemas.reader_book_seeialization import \
    BorrowedBooksListResponse


async def get_active_borrows_by_reader(
        reader_id: int, db: AsyncSession
) -> BorrowedBooksListResponse:
    """
    Возвращает список актуальных книг у читателя.

    Загружает читателя по ID.
    Выбирает все книги, которые он взял и не вернул.
    :return:
        BorrowedBooksListResponse: Список активных книг у читателя.
    """
    reader = await get_reader_by_id(reader_id=reader_id, db=db)
    stmt = select(ReaderBook).where(
        and_(
            ReaderBook.reader_id == reader.id,
            ReaderBook.return_date.is_(None)
        )
    )
    result = await db.execute(stmt)
    books = result.scalars().all()
    return BorrowedBooksListResponse(borrowed_books=books)
