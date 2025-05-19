"""Сериализаторы читателей."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ReaderBase(BaseModel):
    """Базовая модель читателя с основными полями."""

    name: str = Field(..., max_length=255)
    email: EmailStr
    note: Optional[str] = Field(None, max_length=500)


class ReaderCreate(ReaderBase):
    """Модель для создания нового читателя."""


class ReaderUpdate(BaseModel):
    """Модель для обновления данных читателя."""

    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    note: Optional[str] = Field(None, max_length=500)


class ReaderResponse(ReaderBase):
    """Модель ответа с данными читателя, включая ID."""

    id: int

    model_config = ConfigDict(from_attributes=True)
