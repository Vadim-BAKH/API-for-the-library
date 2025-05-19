"""Сериализация модели ошибок."""

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """Базовая модель ошибки."""

    result: bool
    error_type: str
    error_message: str

    model_config = ConfigDict(from_attributes=True)
