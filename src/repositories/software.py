from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.logger import get_logger
from src.models import License, Software


logger = get_logger()


class SoftwareRepo:
    async def get_all(self, session: AsyncSession) -> list[Software]:
        query = select(Software).options(joinedload(Software.sw_type))
        return (await session.scalars(query)).all()

    async def get_by_id(self, session: AsyncSession, software_id: int) -> Software:
        query = select(Software).where(Software.software_id == software_id)
        return await session.scalar(query)

    async def get_with_licenses(self, session: AsyncSession, date: datetime) -> list[Software]:
        query = (
            select(Software)
            .join(Software.licenses)
            .where(and_(License.start_date <= date, License.end_date >= date))
            .options(joinedload(Software.licenses), joinedload(Software.sw_type))
            .order_by(Software.code, License.start_date)
        )
        return (await session.scalars(query)).unique().all()

    async def create(self, session: AsyncSession, model: Software) -> Software:
        session.add(model)
        try:
            await session.flush()
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("Software already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model
