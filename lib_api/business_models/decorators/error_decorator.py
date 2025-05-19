"""Централизация обработки ошибок."""

from functools import wraps

from fastapi import HTTPException, status
from jose import JWTError
from psycopg2 import IntegrityError as pgIntegrityError
from sqlalchemy.exc import IntegrityError, InvalidRequestError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound

from lib_api.factories import error_factory


def handle_db_exceptions(func):
    """Декорирует ошибки функций."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        db: AsyncSession = kwargs.get("db")

        try:
            return await func(*args, **kwargs)

        except NoResultFound as nrf:
            await error_factory.handle_db_error(
                db=db,
                error=nrf,
                er_type="NotFoundError",
                message="Not Found Error",
                st_code=status.HTTP_404_NOT_FOUND,
            )

        except InvalidRequestError as ire:
            await error_factory.handle_db_error(
                db=db,
                error=ire,
                er_type="RequestError",
                message="Request error",
                st_code=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as val:
            await error_factory.handle_db_error(
                db=db,
                error=val,
                er_type="ValueError",
                message=str(val),
                st_code=status.HTTP_404_NOT_FOUND,
            )

        except (IntegrityError, pgIntegrityError) as ine:
            await error_factory.handle_db_error(
                db=db,
                error=ine,
                er_type="UniquenessError",
                message="Uniqueness error",
                st_code=status.HTTP_409_CONFLICT,
            )

        except JWTError as jwt_err:
            await error_factory.handle_db_error(
                db=db,
                error=jwt_err,
                er_type="JWTError",
                message="Could not validate credentials",
                st_code=status.HTTP_401_UNAUTHORIZED,
            )

        except SQLAlchemyError as sql:
            await error_factory.handle_db_error(
                db=db,
                error=sql,
                er_type="DatabaseError",
                message="Database Error",
                st_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except ConnectionError as cne:
            await error_factory.handle_db_error(
                db=db,
                error=cne,
                er_type="ConnectionError",
                message="Connection Error",
                st_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except TimeoutError as toe:
            await error_factory.handle_db_error(
                db=db,
                error=toe,
                er_type="TimeoutError",
                message="Timeout Error",
                st_code=status.HTTP_504_GATEWAY_TIMEOUT,
            )

        except HTTPException as http_exc:
            await error_factory.handle_db_error(
                db=db,
                error=http_exc,
                er_type="HTTPException",
                message=http_exc.detail,
                st_code=http_exc.status_code,
            )

    return wrapper
