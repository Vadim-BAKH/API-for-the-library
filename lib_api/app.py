"""Приложение FastApi."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lib_api.business_models.base_model.base_model import Base
from lib_api.database import async_engine
from lib_api.logs import logger
from lib_api.routing import router as tasks_router


@asynccontextmanager
async def database_life_cycle(api: FastAPI) -> AsyncIterator:
    """
    Асинхронное соединение с базой движка.

    Устанавливает и закрывает соединение.
    Создает таблицы моделей, если их нет.
    """
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    #     logger.info(f"Tables are successfully created with {api}")
    yield
    await async_engine.dispose()

app = FastAPI(lifespan=database_life_cycle)
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # разрешённые источники
    allow_credentials=True,
    allow_methods=["*"],        # разрешённые HTTP методы
    # allow_headers=["*"],
    allow_headers=["Content-Type", "X-My-Fancy-Header"],
    expose_headers=["Content-Type", "X-Custom-Header"],
)

app.include_router(tasks_router)
