from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import get_logger
from src.models import User


logger = get_logger()


class UserRepo:
    async def get_all(self, session: AsyncSession) -> list[User]:
        query = select(User)
        return (await session.scalars(query)).all()

    async def get_by_username(self, session: AsyncSession, username: str) -> User:
        query = select(User).where(User.username == username)
        return await session.scalar(query)

    async def get_by_id(self, session: AsyncSession, user_id: int) -> User:
        query = select(User).where(User.user_id == user_id)
        return await session.scalar(query)

    async def create(self, session: AsyncSession, model: User) -> User:
        session.add(model)
        try:
            await session.flush()
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("User already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model

    async def update(self, session: AsyncSession, model: User) -> User:
        try:
            await session.merge(model)
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("User already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model

    async def delete(self, session: AsyncSession, model: User) -> None:
        try:
            await session.delete(model)
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB deleting error") from err
