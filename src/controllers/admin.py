from hashlib import sha256

from sqlalchemy.ext.asyncio import AsyncSession

from settings import Settings
from src.enums import UserRole
from src.exceptions import ServiceConflict, ServiceNotFound
from src.models import AuditLog, SoftwareType, User
from src.repositories.audit_logs import AuditLogRepo
from src.repositories.software_types import SoftwareTypeRepo
from src.repositories.users import UserRepo


class AdminController:
    def __init__(
        self,
        settings: Settings,
        users: UserRepo,
        sw_types: SoftwareTypeRepo,
        audit_logs: AuditLogRepo,
    ) -> None:
        self._settings = settings
        self._users = users
        self._sw_types = sw_types
        self._audit_logs = audit_logs

    async def create_user(
        self,
        session: AsyncSession,
        token: dict,
        username: str,
        password: str,
        role: UserRole,
        full_name: str,
    ) -> User:
        hashed_pass = sha256(password.encode()).hexdigest()
        model = User(username=username, password=hashed_pass, role=role, full_name=full_name)
        try:
            model = await self._users.create(session, model)
            await self._audit_logs.create(
                session, AuditLog(user_id=token["user_id"], action=f"User created: {username}")
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()
        return model

    async def update_user(
        self,
        session: AsyncSession,
        token: dict,
        user_id: int,
        username: str,
        role: UserRole,
        full_name: str,
    ) -> User:
        existing = await self._users.get_by_id(session, user_id)
        if not existing:
            raise ServiceNotFound(f"User {username} not found")

        existing.username = username
        existing.role = role
        existing.full_name = full_name

        try:
            await self._users.update(session, existing)
            await self._audit_logs.create(
                session, AuditLog(user_id=token["user_id"], action=f"User updated: {username}")
            )
        except ValueError as err:
            raise ServiceConflict(err) from err

        await session.commit()
        return existing

    async def delete_user(self, session: AsyncSession, token: dict, user_id: int) -> None:
        existing = await self._users.get_by_id(session, user_id)

        if not existing:
            raise ServiceNotFound(f"User with ID:{user_id} not found")

        try:
            await self._users.delete(session, existing)
            await self._audit_logs.create(
                session,
                AuditLog(user_id=token["user_id"], action=f"User deleted: {existing.username}"),
            )
        except ValueError as err:
            raise ServiceConflict(err) from err

        await session.commit()

    async def create_sw_type(self, session: AsyncSession, token: dict, name: str) -> SoftwareType:
        model = SoftwareType(name=name)
        try:
            model = await self._sw_types.create(session, model)
            await self._audit_logs.create(
                session, AuditLog(user_id=token["user_id"], action=f"Software type created: {name}")
            )
        except ValueError as err:
            raise ServiceConflict(err) from err
        await session.commit()
        return model

    async def get_audit_logs(self, session: AsyncSession, limit: int) -> list[AuditLog]:
        try:
            models = await self._audit_logs.get_many(session, limit)
        except ValueError as err:
            raise ServiceConflict(err) from err
        return models
