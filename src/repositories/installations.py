from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.logger import get_logger
from src.models import Installation, License, Software


logger = get_logger()


class InstallationRepo:
    async def get_by_id(self, session: AsyncSession, installation_id: int) -> Installation:
        query = select(Installation).where(Installation.installation_id == installation_id)
        return await session.scalar(query)

    async def get_with_software(self, session: AsyncSession, date: datetime) -> list[Installation]:
        query = (
            select(Installation)
            .where(Installation.install_date <= date)
            .options(
                joinedload(Installation.license)
                .subqueryload(License.software)
                .subqueryload(Software.sw_type)
            )
        )
        return (await session.scalars(query)).all()

    async def create(self, session: AsyncSession, model: Installation) -> Installation:
        session.add(model)
        try:
            await session.flush()
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("Installation already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model
