from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.logger import get_logger
from src.models import AuditLog


logger = get_logger()


class AuditLogRepo:
    async def get_many(self, session: AsyncSession, limit: int = 50) -> list[AuditLog]:
        query = select(AuditLog).options(joinedload(AuditLog.user)).limit(limit)
        try:
            models = (await session.scalars(query)).all()
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        return models

    async def create(self, session: AsyncSession, model: AuditLog) -> AuditLog:
        session.add(model)
        try:
            await session.flush()
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("Audit Log already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model
