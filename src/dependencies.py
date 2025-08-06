import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from settings import settings
from src.controllers.admin import AdminController
from src.controllers.login import LoginController
from src.controllers.manager import ManagerController
from src.controllers.supervisor import SupervisorController
from src.exceptions import ServiceConflict, ServiceUnauthorized
from src.repositories.audit_logs import AuditLogRepo
from src.repositories.computer_assignments import ComputerAssignmentRepo
from src.repositories.computers import ComputerRepo
from src.repositories.departments import DepartmentRepo
from src.repositories.installations import InstallationRepo
from src.repositories.licenses import LicenseRepo
from src.repositories.software import SoftwareRepo
from src.repositories.software_types import SoftwareTypeRepo
from src.repositories.users import UserRepo
from src.repositories.vendor import VendorRepo


root_engine = create_async_engine(
    settings.sql_root_url, echo=settings.db_echo, pool_recycle=3600, pool_pre_ping=True
)
admin_engine = create_async_engine(
    settings.sql_admin_url, echo=settings.db_echo, pool_recycle=3600, pool_pre_ping=True
)
manager_engine = create_async_engine(
    settings.sql_manager_url, echo=settings.db_echo, pool_recycle=3600, pool_pre_ping=True
)
supervisor_engine = create_async_engine(
    settings.sql_supervisor_url, echo=settings.db_echo, pool_recycle=3600, pool_pre_ping=True
)

root_session = async_sessionmaker(root_engine, expire_on_commit=False)
admin_session = async_sessionmaker(admin_engine, expire_on_commit=False)
manager_session = async_sessionmaker(manager_engine, expire_on_commit=False)
supervisor_session = async_sessionmaker(supervisor_engine, expire_on_commit=False)

session_map = {
    "root": root_session,
    "admin": admin_session,
    "manager": manager_session,
    "supervisor": supervisor_session,
}


def get_login_controller():
    return LoginController(settings=settings, users=UserRepo())


def get_admin_controller():
    return AdminController(
        settings=settings, users=UserRepo(), sw_types=SoftwareTypeRepo(), audit_logs=AuditLogRepo()
    )


def get_manager_controller():
    return ManagerController(
        settings=settings,
        computers=ComputerRepo(),
        departments=DepartmentRepo(),
        computer_assignments=ComputerAssignmentRepo(),
        software=SoftwareRepo(),
        software_types=SoftwareTypeRepo(),
        vendors=VendorRepo(),
        licenses=LicenseRepo(),
        installations=InstallationRepo(),
    )


def get_supervisor_controller():
    return SupervisorController(
        settings=settings, departments=DepartmentRepo(), licenses=LicenseRepo()
    )


def read_token(auth_token: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> dict:
    try:
        payload = jwt.decode(
            auth_token.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as err:
        raise ServiceUnauthorized("Token expired") from err
    except jwt.InvalidTokenError as err:
        raise ServiceUnauthorized("Invalid token") from err
    return payload


async def get_rbac_session(user_data: dict = Depends(read_token)) -> AsyncSession:
    role = user_data["role"]
    sessionmaker = session_map.get(role)
    if not sessionmaker:
        raise ServiceConflict(f"No sessionmaker for role: {role}")

    async with sessionmaker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_root_session() -> AsyncSession:
    sessionmaker = session_map["root"]
    async with sessionmaker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
