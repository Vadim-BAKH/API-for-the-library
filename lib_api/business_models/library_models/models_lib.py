"""Бизнес модели библиотечного процесса."""

from datetime import datetime

from sqlalchemy import (TIMESTAMP, CheckConstraint, ForeignKey, Integer,
                        String, func, text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib_api.business_models.base_model.base_model import BaseModel


class Book(BaseModel):
    """
    Модель книги.

    Attributes:
        title (str): Название книги.
        author (str): Автор книги.
        publication_year (int | None): Год публикации книги, если известен.
        isbn (str | None): Уникальный международный стандартный номер книги.
        copies_count (int):
                          Количество доступных копий книги.
        readers (list[Reader]):
                              Список читателей, связанных с книгой.
    """

    __tablename__ = "books"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    publication_year: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    isbn: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True
    )
    copies_count: Mapped[int] = mapped_column(
        Integer, server_default=text("1"), nullable=False
    )
    # description: Mapped[str | None] = mapped_column(
    #     String(500), nullable=True
    # )

    __table_args__ = (
        CheckConstraint(
            'copies_count >= 0', name='check_copies_non_negative'
        ),
    )

    reader_books = relationship(
        "ReaderBook",
        back_populates="book",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    readers = relationship(
        "Reader",
        secondary="readers_books",
        viewonly=True,
        back_populates="books",
        lazy="selectin",
    )

    def __repr__(self):
        """
        Возвращает строковое представление объекта книги.

        :return:
                str: Строка в формате <Book(id=ID, title=TITLE, author=AUTHOR)>
        """
        return (f"<Book(id={self.id},"
                f" title={self.title},"
                f" author={self.author})>")


class Reader(BaseModel):
    """
    Модель, представляющая читателя.

    Attributes:
        name (str): Имя читателя.
        email (str): Уникальный email адрес читателя.
        note (str | None): Дополнительная заметка о читателе.
        books (list[Book]): Список книг, связанных с читателем.
    """

    __tablename__ = "readers"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    reader_books = relationship(
        "ReaderBook",
        back_populates="reader",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    books = relationship(
        "Book",
        secondary="readers_books",
        viewonly=True,
        back_populates="readers",
        lazy="selectin",
    )

    def __repr__(self):
        """
        Возвращает строковое представление объекта читателя.

        :return:
           str: Строка в формате <Reader(id=ID, name=NAME, email=EMAIL)>
        """
        return f"<Reader(id={self.id}, name={self.name}, email={self.email})>"


class ReaderBook(BaseModel):
    """
    Модель промежуточной таблицы.

    Связь многие-ко-многим между читателями и книгами.
    Attributes:
        reader_id (int): Внешний ключ на таблицу читателей.
        book_id (int): Внешний ключ на таблицу книг.
    """

    __tablename__ = "readers_books"
    reader_id: Mapped[int] = mapped_column(
        ForeignKey("readers.id", ondelete="CASCADE"),
        nullable=False
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False
    )
    borrow_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    return_date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    reader = relationship(
        "Reader",
        back_populates="reader_books",
        lazy="selectin"
    )
    book = relationship(
        "Book",
        back_populates="reader_books",
        lazy="selectin"
    )
