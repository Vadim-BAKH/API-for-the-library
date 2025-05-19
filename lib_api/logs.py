"""Конфигурация логирования."""

import sys
from os import getenv

from loguru import logger

LOGLEVEL = (getenv("LOGLEVEL") or "DEBUG").upper()

logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
    level=LOGLEVEL,
    enqueue=True,
    serialize=True,
)
