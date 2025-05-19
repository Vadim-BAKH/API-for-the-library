"""Создание читателя."""

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.decorators.error_decorator import \
    handle_db_exceptions
from lib_api.business_models.library_models.models_lib import Reader
from lib_api.business_models.library_models.reader_crud.reader_by_mail import \
    get_reader_by_email
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger
from lib_api.schemas.reader_serialization import ReaderCreate, ReaderResponse


@handle_db_exceptions
async def create_reader(
        reader_in: ReaderCreate, db: AsyncSession
) -> ReaderResponse:
    """
    Создает нового читателя в базе данных.

    Проверяет, что читатель с таким email еще не зарегистрирован.
    Если email уже существует, вызывает обработчик ошибки с кодом 409.
    :return:
        ReaderResponse: сериализованные данные созданного читателя.
    """
    existing = await get_reader_by_email(
        email=str(reader_in.email), db=db
    )
    if existing:
        logger.warning(
            f"Librarian with email {reader_in.email}"
            f" already registered"
        )
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="ValueError",
            message="Email already registered",
            st_code=status.HTTP_409_CONFLICT,
        )
    reader = Reader(
        name=reader_in.name,
        email=reader_in.email,
        note=reader_in.note
    )
    db.add(reader)
    await db.commit()
    await db.refresh(reader)
    return ReaderResponse.model_validate(reader)
