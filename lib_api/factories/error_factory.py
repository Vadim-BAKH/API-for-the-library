"""Фабрика ошибок."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.logs import logger
from lib_api.schemas.error_serialization import ErrorResponse


async def handle_db_error(
    db: AsyncSession,
        error: Exception,
        er_type: str,
        message: str,
        st_code: int
) -> None:
    """Обрабатывает исключения к запросам."""
    await db.rollback()
    logger.error(f"{er_type}: {error}")
    if isinstance(message, dict):
        message = message.get('error_message', str(message))
    problem = ErrorResponse(
        result=False, error_type=er_type, error_message=message
    )
    raise HTTPException(
        status_code=st_code, detail=problem.model_dump()
    ) from error
