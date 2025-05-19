"""Модуль аутентификации читателя."""

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.decorators.error_decorator import \
    handle_db_exceptions
from lib_api.business_models.librarian.librarian_model import Librarian
from lib_api.business_models.librarian.security import verify_password
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger
from lib_api.schemas.librarian_serialization import LibrarianLogin


@handle_db_exceptions
async def get_librarian_by_auth(
        user_auth: LibrarianLogin, db: AsyncSession) -> Librarian:
    """
    Получает библиотекаря по данным аутентификации.

    :return:
        Librarian: Объект библиотекаря при успешной аутентификации.

    Raises:
        ValueError: При отсутствии библиотекаря с таким email.
        При неверном пароле.
    """
    result = await db.execute(
        select(Librarian).where(Librarian.email == user_auth.email)
    )
    librarian = result.scalars().first()
    if not librarian:
        logger.error("Librarian with souch email or password not found")
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="ValueError",
            message="Librarian Not Found",
            st_code=status.HTTP_401_UNAUTHORIZED,
        )
    if not verify_password(
            plain_password=user_auth.password.get_secret_value(),
            hashed_password=str(librarian.password)
    ):
        logger.error(f"Invalid password for librarian {user_auth.email}")
        await handle_db_error(
            db=db,
            error=ValueError(),
            er_type="ValueError",
            message="Librarian Not Found",
            st_code=status.HTTP_401_UNAUTHORIZED,
        )
    logger.debug(f"Librarian with email {user_auth.email} found")
    return librarian
