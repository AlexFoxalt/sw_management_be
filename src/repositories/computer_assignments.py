from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import get_logger
from src.models import ComputerAssignment


logger = get_logger()


class ComputerAssignmentRepo:
    async def create(self, session: AsyncSession, model: ComputerAssignment) -> ComputerAssignment:
        session.add(model)
        try:
            await session.flush()
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("Computer Assignment already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model
