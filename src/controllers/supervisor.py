from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from settings import Settings
from src.exceptions import ServiceNotFound
from src.models import Computer, License, Software
from src.repositories.departments import DepartmentRepo
from src.repositories.licenses import LicenseRepo


class SupervisorController:
    def __init__(
        self, settings: Settings, departments: DepartmentRepo, licenses: LicenseRepo
    ) -> None:
        self._settings = settings
        self._departments = departments
        self._licenses = licenses

    async def get_dept_installed_sw(self, session: AsyncSession, dept_id: int) -> list[Software]:
        model = await self._departments.get_by_id_with_software(session, dept_id)
        if not model:
            raise ServiceNotFound(f"Department with ID:{dept_id} not found")

        result = set()
        for ca in model.assignments:
            computer: Computer = ca.computer
            for inst in computer.installations:
                lcns: License = inst.license
                result.add(lcns.software)
        return list(result)

    async def get_dept_computer_assignments(
        self, session: AsyncSession, dept_id: int
    ) -> list[Computer]:
        model = await self._departments.get_computers(session, dept_id)
        if not model:
            return []
        return [i.computer for i in model.assignments]

    async def get_expiring_licenses(
        self, session: AsyncSession, start_date: datetime, end_date: datetime
    ) -> list[License]:
        return await self._licenses.get_expiring(session, start_date, end_date)
