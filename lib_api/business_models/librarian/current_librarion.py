"""Модуль аутентификации и получения текущего библиотекаря."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lib_api.business_models.decorators.error_decorator import \
    handle_db_exceptions
from lib_api.business_models.librarian.librarian_model import Librarian
from lib_api.business_models.librarian.security import ALGORITHM, SECRET_KEY
from lib_api.database import get_session_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/librarian/oauth2-login")


@handle_db_exceptions
async def get_current_librarian(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session_db)
) -> Librarian:
    """
    Получает текущего авторизованного библиотекаря из JWT токена.

    Декодирует JWT токен, извлекает email библиотекаря.
    Загружает его из базы данных.
    :return:
        Librarian: Объект текущего авторизованного библиотекаря.
    Raises:
        JWTError: Если токен недействителен или истек.
        ValueError: Если библиотекарь с указанным email не найден.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    result = await db.execute(
        select(Librarian).where(Librarian.email == email)
    )
    librarian = result.scalars().first()

    return librarian
