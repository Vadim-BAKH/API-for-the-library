"""Хеширования пароля и создание JWT токена доступа."""

from datetime import datetime, timedelta
from os import getenv
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv(
    "ACCESS_TOKEN_EXPIRE_MINUTES")
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(
        plain_password: str, hashed_password: str
) -> bool:
    """
    Проверяет соответствие простого пароля и его хэша.

    Args:
        plain_password (str): Обычный текстовый пароль.
        hashed_password (str): Хэш пароля для проверки.

    :return:
        bool: True, если пароль совпадает с хэшем, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хэширует пароль с использованием bcrypt.

    Args:
        password (str): Пароль для хэширования.
    :return:
        str: Хэшированный пароль.
    """
    return pwd_context.hash(password)


def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает JWT токен доступа.

    Указаны данные и время жизни.
    Args:
        data (dict): Данные для кодирования в токен
        (например, идентификатор пользователя).
        expires_delta (Optional[timedelta]): Время жизни токена.
        Если не указано, используется 15 минут.
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
