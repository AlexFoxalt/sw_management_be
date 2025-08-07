from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from settings import Settings
from src.enums import ComputerType
from src.exceptions import ServiceConflict, ServiceNotFound
from src.models import (
    AuditLog,
    Computer,
    ComputerAssignment,
    Installation,
    License,
    Software,
    Vendor,
)
from src.repositories.audit_logs import AuditLogRepo
from src.repositories.computer_assignments import ComputerAssignmentRepo
from src.repositories.computers import ComputerRepo
from src.repositories.departments import DepartmentRepo
from src.repositories.installations import InstallationRepo
from src.repositories.licenses import LicenseRepo
from src.repositories.software import SoftwareRepo
from src.repositories.software_types import SoftwareTypeRepo
from src.repositories.vendor import VendorRepo


class ManagerController:
    def __init__(
        self,
        settings: Settings,
        computers: ComputerRepo,
        departments: DepartmentRepo,
        computer_assignments: ComputerAssignmentRepo,
        software: SoftwareRepo,
        software_types: SoftwareTypeRepo,
        vendors: VendorRepo,
        licenses: LicenseRepo,
        installations: InstallationRepo,
        audit_logs: AuditLogRepo,
    ) -> None:
        self._settings = settings
        self._computers = computers
        self._departments = departments
        self._computer_assignments = computer_assignments
        self._software = software
        self._software_types = software_types
        self._vendors = vendors
        self._licenses = licenses
        self._installations = installations
        self._audit_logs = audit_logs

    async def create_computer(
        self,
        session: AsyncSession,
        token: dict,
        inventory_number: str,
        computer_type: ComputerType,
        purchase_date: datetime,
        status: str,
    ) -> Computer:
        model = Computer(
            inventory_number=inventory_number,
            computer_type=computer_type,
            purchase_date=purchase_date,
            status=status,
        )
        try:
            model = await self._computers.create(session, model)
            await self._audit_logs.create(
                session,
                AuditLog(user_id=token["user_id"], action=f"Computer created: {inventory_number}"),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()
        return model

    async def create_computer_assignment(
        self,
        session: AsyncSession,
        token: dict,
        computer_id: int,
        dept_id: int,
        start_date: datetime,
        end_date: datetime | None,
        doc_number: str,
        doc_date: datetime,
        doc_type: str,
    ) -> ComputerAssignment:
        computer = await self._computers.get_by_id(session, computer_id)
        if not computer:
            raise ServiceNotFound(f"Computer with ID:{computer_id} not found")

        department = await self._departments.get_by_id(session, dept_id)
        if not department:
            raise ServiceNotFound(f"Department with ID:{dept_id} not found")

        model = ComputerAssignment(
            computer=computer,
            department=department,
            start_date=start_date,
            end_date=end_date,
            doc_number=doc_number,
            doc_date=doc_date,
            doc_type=doc_type,
        )
        try:
            model = await self._computer_assignments.create(session, model)
            await self._audit_logs.create(
                session,
                AuditLog(
                    user_id=token["user_id"], action=f"Computer assignment created: {doc_number}"
                ),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()
        return model

    async def delete_computer(self, session: AsyncSession, token: dict, computer_id: int) -> None:
        existing = await self._computers.get_by_id(session, computer_id)

        if not existing:
            raise ServiceNotFound(f"Computer with ID:{computer_id} not found")

        try:
            await self._computers.delete(session, existing)
            await self._audit_logs.create(
                session,
                AuditLog(
                    user_id=token["user_id"],
                    action=f"Computer deleted: {existing.inventory_number}",
                ),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err

        await session.commit()

    async def create_software(
        self,
        session: AsyncSession,
        token: dict,
        sw_type_id: int,
        code: str,
        name: str,
        short_name: str | None,
        manufacturer: str,
    ) -> Software:
        sw_type = await self._software_types.get_by_id(session, sw_type_id)
        if not sw_type:
            raise ServiceNotFound(f"Software Type with ID:{sw_type_id} not found")

        model = Software(
            sw_type=sw_type, code=code, name=name, short_name=short_name, manufacturer=manufacturer
        )
        try:
            model = await self._software.create(session, model)
            await self._audit_logs.create(
                session, AuditLog(user_id=token["user_id"], action=f"Software created: {name}")
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()
        return model

    async def create_license(
        self,
        session: AsyncSession,
        token: dict,
        software_id: int,
        vendor_id: int,
        start_date: datetime,
        end_date: datetime,
        price_per_unit: float,
    ) -> License:
        software = await self._software.get_by_id(session, software_id)
        if not software:
            raise ServiceNotFound(f"Software with ID:{software_id} not found")

        vendor = await self._vendors.get_by_id(session, vendor_id)
        if not vendor:
            raise ServiceNotFound(f"Vendor with ID:{vendor_id} not found")

        model = License(
            software=software,
            vendor=vendor,
            start_date=start_date,
            end_date=end_date,
            price_per_unit=price_per_unit,
        )
        try:
            model = await self._licenses.create(session, model)
            await self._audit_logs.create(
                session,
                AuditLog(
                    user_id=token["user_id"],
                    action=f"License created: {software.name} by {vendor.name}",
                ),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()
        return model

    async def create_installation(
        self,
        session: AsyncSession,
        token: dict,
        license_id: int,
        computer_id: int,
        install_date: datetime,
    ) -> Installation:
        license_model = await self._licenses.get_by_id(session, license_id)
        if not license_model:
            raise ServiceNotFound(f"License with ID:{license_id} not found")

        computer = await self._computers.get_by_id(session, computer_id)
        if not computer:
            raise ServiceNotFound(f"Computer with ID:{computer_id} not found")

        model = Installation(license=license_model, computer=computer, install_date=install_date)
        try:
            model = await self._installations.create(session, model)
            await self._audit_logs.create(
                session,
                AuditLog(
                    user_id=token["user_id"],
                    action=f"Installation created: {license_model.software} on {computer.inventory_number}",
                ),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()
        return model

    async def get_computer_software(
        self, session: AsyncSession, token: dict, computer_id: int
    ) -> list[Software]:
        model = await self._computers.get_software(session, computer_id)

        try:
            await self._audit_logs.create(
                session,
                AuditLog(
                    user_id=token["user_id"],
                    action=f"Computer software retrieved: {model.inventory_number}",
                ),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()

        if not model:
            return []
        return [i.license.software for i in model.installations]

    async def create_vendor(
        self, session: AsyncSession, token: dict, name: str, address: str, phone: str, website: str
    ) -> Vendor:
        model = Vendor(name=name, address=address, phone=phone, website=website)
        try:
            model = await self._vendors.create(session, model)
            await self._audit_logs.create(
                session, AuditLog(user_id=token["user_id"], action=f"Vendor created: {name}")
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()
        return model

    async def gen_installed_sw_report(
        self, session: AsyncSession, token: dict, date: datetime
    ) -> list[dict]:
        models = await self._installations.get_with_software(session, date)
        data = []
        for m in models:
            lcns: License = m.license
            sw: Software = lcns.software
            data.append(
                {
                    "install_date": m.install_date.isoformat(),
                    "license_start_date": lcns.start_date.isoformat(),
                    "license_end_date": lcns.end_date.isoformat(),
                    "sw_name": sw.name,
                    "sw_code": sw.code,
                    "sw_type": sw.sw_type.name,
                }
            )

        try:
            await self._audit_logs.create(
                session,
                AuditLog(user_id=token["user_id"], action="Installed software report generated"),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()

        return data

    async def gen_counted_sw_licenses_report(
        self, session: AsyncSession, token: dict, date: datetime
    ) -> list[dict]:
        models = await self._software.get_with_licenses(session, date)
        data = []
        for m in models:
            data.append(
                {
                    "software_id": m.software_id,
                    "sw_type_id": m.sw_type_id,
                    "sw_type_name": m.sw_type.name,
                    "code": m.code,
                    "name": m.name,
                    "short_name": m.short_name,
                    "manufacturer": m.manufacturer,
                    "total_licenses": len(m.licenses),
                }
            )

        try:
            await self._audit_logs.create(
                session,
                AuditLog(
                    user_id=token["user_id"], action="Software licenses count report generated"
                ),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()

        return data

    async def gen_counted_depts_comps_report(
        self, session: AsyncSession, token: dict, date: datetime
    ) -> list[dict]:
        models = await self._departments.get_with_assignments(session, date)
        data = []
        for m in models:
            data.append(
                {
                    "dept_id": m.dept_id,
                    "dept_code": m.dept_code,
                    "dept_name": m.dept_name,
                    "dept_short_name": m.dept_short_name,
                    "total_computers": len(m.assignments),
                }
            )

        try:
            await self._audit_logs.create(
                session,
                AuditLog(
                    user_id=token["user_id"],
                    action="Department assigned computers report generated",
                ),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()

        return data
