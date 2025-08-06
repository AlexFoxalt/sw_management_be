import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import CreateTable

from src.models import *


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/mydb"
engine = create_async_engine(DATABASE_URL, echo=False)


def preview_ddl():
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=engine.dialect))
        print(f"\n-- DDL for table `{table.name}` --")
        print(ddl)
        print("-- End of DDL --")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    preview_ddl()
    asyncio.run(create_tables())
