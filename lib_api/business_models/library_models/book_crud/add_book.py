"""Создание книги."""

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.decorators.error_decorator import \
    handle_db_exceptions
from lib_api.business_models.library_models.book_crud.check_isbn import \
    get_book_by_isbn
from lib_api.business_models.library_models.models_lib import Book
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger
from lib_api.schemas.book_serialization import BookCreate, BookResponse


@handle_db_exceptions
async def create_book(
    book_in: BookCreate,
    db: AsyncSession
) -> BookResponse:
    """
    Создает книгу в базе данных.

    Проверяет, что читатель с таким isbn еще не зарегистрирована.
    :raise: Обработчик ошибки с кодом 409.
    :return:
        ReaderResponse: сериализованные данные книги.
    """
    if book_in.isbn:
        existing = await get_book_by_isbn(isbn=book_in.isbn, db=db)
        if existing:
            logger.warning(f"Book with ISBN {book_in.isbn} already exists")
            await handle_db_error(
                db=db,
                error=ValueError("ISBN already registered"),
                er_type="ISBNRegistered",
                message="Isbn already registered",
                st_code=status.HTTP_409_CONFLICT,
            )

    book = Book(
        title=book_in.title,
        author=book_in.author,
        publication_year=book_in.publication_year,
        isbn=book_in.isbn,
        copies_count=book_in.copies_count
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return BookResponse.model_validate(book)
