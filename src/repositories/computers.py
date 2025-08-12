from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.logger import get_logger
from src.models import Computer, ComputerAssignment, Installation, License, Software


logger = get_logger()


class ComputerRepo:
    async def get_all(self, session: AsyncSession) -> list[Computer]:
        query = select(Computer).options(
            joinedload(Computer.assignment).subqueryload(ComputerAssignment.department)
        )
        return (await session.scalars(query)).unique().all()

    async def get_by_id(self, session: AsyncSession, computer_id: int) -> Computer:
        query = select(Computer).where(Computer.computer_id == computer_id)
        return await session.scalar(query)

    async def get_software(self, session: AsyncSession, computer_id: int) -> Computer:
        query = (
            select(Computer)
            .where(Computer.computer_id == computer_id)
            .options(
                joinedload(Computer.installations)
                .subqueryload(Installation.license)
                .subqueryload(License.software)
                .subqueryload(Software.sw_type)
            )
        )
        return await session.scalar(query)

    async def create(self, session: AsyncSession, model: Computer) -> Computer:
        session.add(model)
        try:
            await session.flush()
        except IntegrityError as err:
            logger.error(f"Integrity error: {err}")
            raise ValueError("Computer already exists") from err
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB writing error") from err
        return model

    async def delete(self, session: AsyncSession, model: Computer) -> None:
        try:
            await session.delete(model)
        except ProgrammingError as err:
            logger.error(f"Programming error: {err}")
            raise ValueError("Insufficient permissions") from err
        except SQLAlchemyError as err:
            logger.error(f"Generic SQLAlchemy error: {err}")
            raise ValueError("DB deleting error") from err
