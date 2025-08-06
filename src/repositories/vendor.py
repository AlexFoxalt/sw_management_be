from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import get_logger
from src.models import Vendor


logger = get_logger()


class VendorRepo:
    async def get_by_id(self, session: AsyncSession, vendor_id: int) -> Vendor:
        query = select(Vendor).where(Vendor.vendor_id == vendor_id)
        return await session.scalar(query)

    async def create(self, session: AsyncSession, model: Vendor) -> Vendor:
        session.add(model)
        try:
            await session.flush()
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("Vendor already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model
