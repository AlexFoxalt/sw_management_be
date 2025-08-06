from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import get_logger
from src.models import SoftwareType


logger = get_logger()


class SoftwareTypeRepo:
    async def get_by_id(self, session: AsyncSession, sw_type_id: int) -> SoftwareType:
        query = select(SoftwareType).where(SoftwareType.sw_type_id == sw_type_id)
        return await session.scalar(query)

    async def create(self, session: AsyncSession, model: SoftwareType) -> SoftwareType:
        session.add(model)
        try:
            await session.flush()
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("Software type already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model
