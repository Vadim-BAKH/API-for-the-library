"""Сериализаторы книги."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, conint


class BookBase(BaseModel):
    """Базовая модель книги с основными полями."""

    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    publication_year: Optional[int] = None
    isbn: Optional[str] = Field(None, max_length=20)
    copies_count: conint(ge=0) = Field(default=1)


class BookCreate(BookBase):
    """Модель для создания новой книги."""


class BookUpdate(BaseModel):
    """Модель для обновления данных книги."""

    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = None
    isbn: Optional[str] = Field(None, max_length=20)
    copies_count: Optional[conint(ge=0)] = None


class BookResponse(BookBase):
    """Модель ответа с данными книги, включая ID."""

    id: int

    model_config = ConfigDict(from_attributes=True)
