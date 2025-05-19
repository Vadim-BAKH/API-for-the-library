"""Удаление читателя."""

from fastapi import status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.decorators.error_decorator import \
    handle_db_exceptions
from lib_api.business_models.library_models.models_lib import ReaderBook
from lib_api.business_models.library_models.reader_crud.reader_by_id import \
    get_reader_by_id
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger


@handle_db_exceptions
async def delete_reader(reader_id: int, db: AsyncSession) -> None:
    """
    Удаляет читателя без активных задач из базы данных.

    Проверяет наличие активных заимствований у читателя.
    На активные заимствования вызывает обработчик ошибки с кодом 400.

    :return: None
    """
    reader = await get_reader_by_id(reader_id, db)
    count_stmt = select(func.count()).select_from(ReaderBook).where(
        and_(
            ReaderBook.reader_id == reader_id,
            ReaderBook.return_date.is_(None)
        )
    )
    result = await db.execute(count_stmt)
    active_count = result.scalar_one()

    if active_count > 0:
        logger.warning(
            f"Bad delete Reader ID {reader_id}."
            f" Reader has active borrowings."
        )
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="BadDeleteReader",
            message="Reader has active borrowings",
            st_code=status.HTTP_400_BAD_REQUEST,
        )

    await db.delete(reader)
    await db.commit()
