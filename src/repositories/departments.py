from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.logger import get_logger
from src.models import Computer, ComputerAssignment, Department, Installation, License, Software


logger = get_logger()


class DepartmentRepo:
    async def get_by_id(self, session: AsyncSession, dept_id: int) -> Department:
        query = select(Department).where(Department.dept_id == dept_id)
        return await session.scalar(query)

    async def get_with_assignments(self, session: AsyncSession, date: datetime) -> list[Department]:
        query = (
            select(Department)
            .join(Department.assignments)
            .where(
                and_(
                    ComputerAssignment.start_date <= date,
                    or_(ComputerAssignment.end_date.is_(None), ComputerAssignment.end_date >= date),
                )
            )
            .options(joinedload(Department.assignments))
            .order_by(Department.dept_code)
        )
        return (await session.scalars(query)).unique().all()

    async def get_computers(self, session: AsyncSession, dept_id: int) -> Department:
        query = (
            select(Department)
            .where(Department.dept_id == dept_id)
            .options(joinedload(Department.assignments).subqueryload(ComputerAssignment.computer))
        )
        return await session.scalar(query)

    async def get_by_id_with_software(self, session: AsyncSession, dept_id: int) -> Department:
        query = (
            select(Department)
            .where(Department.dept_id == dept_id)
            .options(
                joinedload(Department.assignments)
                .subqueryload(ComputerAssignment.computer)
                .subqueryload(Computer.installations)
                .subqueryload(Installation.license)
                .subqueryload(License.software)
                .subqueryload(Software.sw_type)
            )
        )
        return await session.scalar(query)
