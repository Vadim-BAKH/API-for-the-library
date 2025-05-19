"""Обновление данных читателя."""

from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.decorators.error_decorator import \
    handle_db_exceptions
from lib_api.business_models.library_models.reader_crud.reader_by_id import \
    get_reader_by_id
from lib_api.schemas.reader_serialization import ReaderResponse, ReaderUpdate


@handle_db_exceptions
async def update_reader_data(
    reader_id: int,
    reader_in: ReaderUpdate,
    db: AsyncSession
) -> ReaderResponse:
    """
    Обновляет данные читателя по его идентификатору.

    Загружает существующего читателя из базы данных.
    Обновляет указанные поля.
    Сохраняет изменения и возвращает обновленные данные.
    :return:
        ReaderResponse: сериализованные данные читателя.
    """
    reader = await get_reader_by_id(reader_id, db)
    update_data = reader_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reader, field, value)

    db.add(reader)
    await db.commit()
    await db.refresh(reader)
    return ReaderResponse.model_validate(reader)
