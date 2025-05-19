"""Модель библиотекаря."""
from typing import Optional

from fastapi import status
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from lib_api.business_models.base_model.base_model import BaseModel
from lib_api.business_models.decorators.error_decorator import \
    handle_db_exceptions
from lib_api.business_models.librarian.security import get_password_hash
from lib_api.factories.error_factory import handle_db_error
from lib_api.logs import logger
from lib_api.schemas.librarian_serialization import LibrarianCreate


class Librarian(BaseModel):
    """
    Модель, представляющая библиотекаря в системе.

    Attributes:
        name: Полное имя библиотекаря (максимум 100 символов).
        email: Уникальный email-адрес для входа в систему.
        password: Хэшированный пароль для аутентификации.
    """

    __tablename__ = "librarian"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self):
        """
        Возвращает строковое представление объекта библиотекаря.

        :return: Строка в формате: <Librarian(id=ID, email=EMAIL)>
        """
        return f"<Librarian(id={self.id}, email={self.email})>"

    @classmethod
    async def get_librarian_by_email(
            cls, db: AsyncSession, email: str
    ) -> Optional["Librarian"]:
        """
        Поиск библиотекаря по email.

        Args:
            db (AsyncSession): Асинхронная сессия БД
            email (str): Email для поиска

        Returns:
            Librarian | None: Объект библиотекаря или None
        """
        result = await db.execute(
            select(cls).where(cls.email == email)
        )
        return result.scalars().first()

    @classmethod
    @handle_db_exceptions
    async def create_librarian(
            cls, librarian_in: LibrarianCreate, db: AsyncSession
    ) -> "Librarian":
        """
        Создает нового библиотекаря в базе данных.

        Проверяет, что библиотекарь с таким email еще не зарегистрирован.
        Если email уже существует, вызывает обработчик ошибки с кодом 409.
        Хэширует пароль перед сохранением.
        :return:
            Librarian: Созданный объект библиотекаря.
        """
        existing = await cls.get_librarian_by_email(
            db=db, email=str(librarian_in.email)
        )
        if existing:
            logger.warning(
                f"Librarian with email {librarian_in.email}"
                f" already registered"
            )
            await handle_db_error(
                db=db,
                error=ValueError(),
                er_type="ValueError",
                message="Email already registered",
                st_code=status.HTTP_409_CONFLICT,
            )
        hashed_password = get_password_hash(
            password=librarian_in.password.get_secret_value()
        )
        db_librarian = cls(
            name=librarian_in.name,
            email=librarian_in.email,
            password=hashed_password
        )
        db.add(db_librarian)
        await db.commit()
        await db.refresh(db_librarian)
        logger.info(f"Librarian {db_librarian.id} created successfully")
        return db_librarian
