"""Сериализатор библиотекаря."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class LibrarianCreate(BaseModel):
    """Модель для создания нового библиотекаря."""

    name: str = Field(..., max_length=100)
    email: EmailStr
    password: SecretStr = Field(..., min_length=8)


class LibrarianResponse(BaseModel):
    """Модель ответа с данными библиотекаря."""

    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Модель для передачи токена доступа."""

    access_token: str
    token_type: str = "bearer"


class LibrarianLogin(BaseModel):
    """Модель для аутентификации библиотекаря."""

    email: EmailStr
    password: SecretStr
