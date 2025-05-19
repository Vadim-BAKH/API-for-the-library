"""Читатель по ID."""

from typing import Optional

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.library_models.models_lib import Reader
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger


async def get_reader_by_id(
        reader_id: int, db: AsyncSession
) -> Optional[Reader]:
    """
    Получает читателя из базы данных по его идентификатору.

    Если читатель с ID не найден, вызывает обработчик ошибки.
    :return:
       Optional[Reader] - модель читателя опционально.
    """
    result = await db.execute(select(Reader)
                              .where(Reader.id == reader_id))
    reader = result.scalars().first()

    if not reader:
        logger.warning(f"Reader with such ID {reader_id} not found")
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="NotFoundReaderID",
            message="Reader with given ID not found",
            st_code=status.HTTP_404_NOT_FOUND,
        )
    return reader
