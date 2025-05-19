
"""Регистрация маршрутов приложения."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import SecretStr
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.librarian import librarian_model
from lib_api.business_models.librarian.auth_librarian import \
    get_librarian_by_auth
from lib_api.business_models.librarian.current_librarion import \
    get_current_librarian
from lib_api.business_models.librarian.util import get_access_token_for_user
from lib_api.business_models.library_models.book_crud.add_book import \
    create_book
from lib_api.business_models.library_models.book_crud.book_by_id import \
    get_book_by_id
from lib_api.business_models.library_models.book_crud.delete_book import \
    delete_book
from lib_api.business_models.library_models.book_crud.update_book import \
    update_book_data
from lib_api.business_models.library_models.borrow_return_service.books_at_the_reader import \
    get_active_borrows_by_reader
from lib_api.business_models.library_models.borrow_return_service.borrow_book import \
    borrow_book
from lib_api.business_models.library_models.borrow_return_service.return_book import \
    return_book
from lib_api.business_models.library_models.models_lib import Book, Reader
from lib_api.business_models.library_models.reader_crud.add_reader import \
    create_reader
from lib_api.business_models.library_models.reader_crud.delete_reader import \
    delete_reader
from lib_api.business_models.library_models.reader_crud.reader_by_id import \
    get_reader_by_id
from lib_api.business_models.library_models.reader_crud.update_reader import \
    update_reader_data
from lib_api.database import get_session_db
from lib_api.schemas import librarian_serialization, reader_serialization
from lib_api.schemas.book_serialization import (BookCreate, BookResponse,
                                                BookUpdate)
from lib_api.schemas.reader_book_seeialization import (
    BorrowBookRequest, BorrowedBookResponse, BorrowedBooksListResponse,
    ReturnBookRequest)
from lib_api.schemas.reader_serialization import ReaderResponse, ReaderUpdate

router = APIRouter(
    prefix="/api",
)


@router.post(
    "/librarian/oauth2-login",
    response_model=librarian_serialization.Token,
    tags=["Authentication"]
)
async def oauth2_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session_db)
) -> librarian_serialization.Token:
    """
    Авторизует пользователя.

    Возвращает токен.
    """
    user_in = librarian_serialization.LibrarianLogin(
        email=form_data.username,
        password=SecretStr(form_data.password)
    )
    librarian = await get_librarian_by_auth(user_auth=user_in, db=db)
    access_token = await get_access_token_for_user(librarian=librarian)
    return librarian_serialization.Token(access_token=access_token)


@router.post(
    "/librarian/registration",
    status_code=status.HTTP_201_CREATED,
    response_model=librarian_serialization.Token,
    tags=["Authentication"]
)
async def create_new_user(
    user_in: librarian_serialization.LibrarianCreate,
    db: AsyncSession = Depends(get_session_db)
) -> librarian_serialization.Token:
    """
    Регистрирует и создает библиотекаря..

    :return: librarian_serialization.Token: токен.
    """
    db_librarian = await (librarian_model.Librarian
                          .create_librarian(librarian_in=user_in, db=db))
    access_token = await get_access_token_for_user(librarian=db_librarian)
    return librarian_serialization.Token(access_token=access_token)


@router.post(
    "/reader/create",
    response_model=reader_serialization.ReaderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Readers"],
    dependencies=[Depends(get_current_librarian)]
)
async def create_new_reader(
    reader_in: reader_serialization.ReaderCreate,
    db: AsyncSession = Depends(get_session_db)
) -> reader_serialization.ReaderResponse:
    """
    Создает нового читателя в базе данных.

    :return:
        ReaderResponse: Информация о созданном читателе.
    """
    return await create_reader(reader_in=reader_in, db=db)


@router.get(
    "/reader/{reader_id}",
    response_model=ReaderResponse,
    tags=["Readers"],
    dependencies=[Depends(get_current_librarian)]
)
async def read_reader_by_id(
        reader_id: int, db: AsyncSession = Depends(get_session_db)
) -> ReaderResponse:
    """
    Получает информацию о читателе по его ID.

    :return:
        ReaderResponse: Данные читателя с указанным ID.
    """
    reader = await get_reader_by_id(reader_id, db)
    return ReaderResponse.model_validate(reader)


@router.put(
    "/reader/update/{reader_id}",
    response_model=ReaderResponse,
    tags=["Readers"],
    dependencies=[Depends(get_current_librarian)]
)
async def update_existing_reader(
    reader_id: int,
    reader_in: ReaderUpdate,
    db: AsyncSession = Depends(get_session_db)
) -> ReaderResponse:
    """
    Обновляет данные существующего читателя по его ID.

    :return:
        ReaderResponse: Обновленные данные читателя.
    """
    return await update_reader_data(
        reader_id=reader_id, reader_in=reader_in, db=db
    )


@router.delete(
    "/reader/{reader_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Readers"],
    dependencies=[Depends(get_current_librarian)]
)
async def delete_existing_reader(
        reader_id: int, db: AsyncSession = Depends(get_session_db)
) -> None:
    """
    Удаляет существующего читателя по его ID.

    :return:
        None: Возвращает пустой ответ с кодом 204.
    """
    await delete_reader(reader_id=reader_id, db=db)
    return None


@router.get(
    "/readers",
    response_model=Page[ReaderResponse],
    tags=["Readers"],
    dependencies=[Depends(get_current_librarian)]
)
async def list_readers(
    db: AsyncSession = Depends(get_session_db),
    params: Params = Depends()
) -> Page[ReaderResponse]:
    """
    Возвращает постраничный список всех читателей.

    Список сортирован по алфавиту.
    :return:
        Page[ReaderResponse]: Страница с данными читателей.
    """
    query = select(Reader).order_by(asc(Reader.name))
    return await paginate(db, query, params)


@router.post(
    "/book/create",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Books"],
    dependencies=[Depends(get_current_librarian)]
)
async def create_new_book(
    book_in: BookCreate,
    db: AsyncSession = Depends(get_session_db)
) -> BookResponse:
    """
    Создает новую книгу в базе данных.

    :return:
        BookResponse: Информация о созданной книге
    """
    return await create_book(book_in=book_in, db=db)


@router.get(
    "/librarian",
    response_model=Page[BookResponse],
    tags=["Books"],
)
async def list_books(
    db: AsyncSession = Depends(get_session_db),
    params: Params = Depends()
) -> Page[BookResponse]:
    """
    Возвращает постраничный список всех книг.

    Сортировка по LIFO.
    :return:
        Page[BookResponse]: Страница с данными книг.
    """
    query = select(Book).order_by(desc(Book.id))
    return await paginate(db, query, params)


@router.get(
    "/book/{book_id}",
    response_model=BookResponse,
    tags=["Books"],
    dependencies=[Depends(get_current_librarian)]
)
async def read_book_by_id(
    book_id: int,
    db: AsyncSession = Depends(get_session_db)
) -> BookResponse:
    """
    Получает информацию о книге по её ID.

    :return:
        BookResponse: Данные книги с указанным ID.
    """
    book = await get_book_by_id(book_id, db)
    return BookResponse.model_validate(book)


@router.put(
    "/book/update/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    tags=["Books"],
    dependencies=[Depends(get_current_librarian)]
)
async def update_existing_book(
    book_id: int,
    book_in: BookUpdate,
    db: AsyncSession = Depends(get_session_db)
) -> BookResponse:
    """
    Обновляет данные существующей книги по её ID.

    :return:
        BookResponse: Обновленные данные книги.
    """
    return await update_book_data(
        book_id=book_id, book_in=book_in, db=db
    )


@router.delete(
    "/book/delete/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Books"],
    dependencies=[Depends(get_current_librarian)]
)
async def delete_existing_book(
    book_id: int,
    db: AsyncSession = Depends(get_session_db)
) -> None:
    """
    Удаляет книгу из базы данных по её ID.

    :return:
        None: Возвращает пустой ответ с кодом 204.
    """
    await delete_book(book_id=book_id, db=db)
    return None


@router.post(
    "/librarian/borrow",
    response_model=BorrowedBookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Borrow and Return"],
    dependencies=[Depends(get_current_librarian)]
)
async def borrow_book_endpoint(
    borrow_req: BorrowBookRequest,
    db: AsyncSession = Depends(get_session_db)
) -> BorrowedBookResponse:
    """
    Оформляет взятие книги читателем.

    :return:
        BorrowedBookResponse: Информация о взятой книге.
    """
    borrow = await borrow_book(borrow_req.book_id, borrow_req.reader_id, db)
    return borrow


@router.post(
    "/librarian/return",
    response_model=BorrowedBookResponse,
    status_code=status.HTTP_200_OK,
    tags=["Borrow and Return"],
    dependencies=[Depends(get_current_librarian)]
)
async def return_book_endpoint(
    return_req: ReturnBookRequest,
    db: AsyncSession = Depends(get_session_db)
) -> BorrowedBookResponse:
    """
    Оформляет возврат книги, ранее взятой читателем.

    :return:
    BorrowedBookResponse: Информация о возвращенной книге.
    """
    borrow = await return_book(return_req.borrow_id, db)
    return borrow


@router.get(
    "/reader/{reader_id}/borrowed",
    response_model=BorrowedBooksListResponse,
    status_code=status.HTTP_200_OK,
    tags=["Borrow and Return"],
    dependencies=[Depends(get_current_librarian)]
)
async def list_borrowed_books(
    reader_id: int,
    db: AsyncSession = Depends(get_session_db)
) -> BorrowedBooksListResponse:
    """
    Список активных взятых книг для указанного читателя.

    :return:
        BorrowedBooksListResponse: Список взятых книг читателя.
    """
    borrows = await get_active_borrows_by_reader(reader_id, db)
    return borrows
