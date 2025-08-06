from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import AuditLog


class AuditLogRepo:
    async def get_many(self, session: AsyncSession, limit: int = 50) -> list[AuditLog]:
        query = select(AuditLog).limit(limit)
        return (await session.scalars(query)).all()
