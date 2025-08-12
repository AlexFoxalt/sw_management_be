from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.logger import get_logger
from src.models import License


logger = get_logger()


class LicenseRepo:
    async def get_all(self, session: AsyncSession) -> list[License]:
        query = select(License).options(joinedload(License.software), joinedload(License.vendor))
        return (await session.scalars(query)).all()

    async def get_by_id(self, session: AsyncSession, license_id: int) -> License:
        query = (
            select(License)
            .where(License.license_id == license_id)
            .options(joinedload(License.software), joinedload(License.vendor))
        )
        return await session.scalar(query)

    async def get_expiring(
        self, session: AsyncSession, start_date: datetime, end_date: datetime
    ) -> list[License]:
        query = (
            select(License)
            .where(and_(License.end_date >= start_date, License.end_date <= end_date))
            .options(joinedload(License.software), joinedload(License.vendor))
            .order_by(License.end_date)
        )
        return (await session.scalars(query)).all()

    async def create(self, session: AsyncSession, model: License) -> License:
        session.add(model)
        try:
            await session.flush()
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("License already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model
