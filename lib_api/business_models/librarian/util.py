"""Генерация JWT токена для библиотекаря."""

from datetime import timedelta

from lib_api.business_models.librarian.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token)


async def get_access_token_for_user(librarian) -> str:
    """
    Генерирует JWT токен доступа для указанного библиотекаря.

    Args:
        librarian: Объект библиотекаря, для которого создается токен.
                   Должен содержать атрибут email.

    :return:
        librarian: Объект библиотекаря, для которого создается токен.
                   Должен содержать атрибут email.
    """
    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return create_access_token(
        data={"sub": librarian.email},
        expires_delta=access_token_expires
    )
