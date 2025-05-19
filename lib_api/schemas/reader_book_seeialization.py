"""Сериализаторы Выдачи и возврата книг."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BorrowBookRequest(BaseModel):
    """Запрос на взятие книги читателем."""

    book_id: int = Field(..., gt=0)
    reader_id: int = Field(..., gt=0)


class ReturnBookRequest(BaseModel):
    """Запрос на возврат ранее взятой книги."""

    borrow_id: int = Field(..., gt=0)


class BorrowedBookResponse(BaseModel):
    """Ответ с информацией о взятой книге."""

    id: int
    book_id: int
    reader_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BorrowedBooksListResponse(BaseModel):
    """Ответ со списком активных взятых книг."""

    borrowed_books: List[BorrowedBookResponse]
