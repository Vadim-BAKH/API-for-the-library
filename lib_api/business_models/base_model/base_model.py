"""Базовая модель."""


from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для декларативных моделей SQLAlchemy."""


class BaseModel(Base):
    """
    Абстрактная модель с общими полями для всех таблиц.

    Attributes:
        id: Уникальный идентификатор записи (первичный ключ).
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    def __repr__(self) -> str:
        """
        Возвращает строковое представление объекта.

        :return: Строка в формате: <ClassName(id=ID)>
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
