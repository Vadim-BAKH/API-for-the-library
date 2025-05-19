"""Проверка email читателя."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.library_models.models_lib import Reader


async def get_reader_by_email(
        email: str, db: AsyncSession
) -> Optional["Reader"]:
    """
    Получает читателя из базы данных по его email.

    :return:
        Optional[Reader]: Объект читателя, если найден, иначе None.
    """
    result = await db.execute(select(Reader)
                              .where(Reader.email == email))

    return result.scalars().first()
